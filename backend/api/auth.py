# ========================================
# 学生信息管理系统 - 认证API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import uuid

from models import User, UserRole, AuditLog, AuditAction
from schemas import UserSchema, UserLoginSchema, UserPasswordChangeSchema, UserPasswordResetSchema, UserRegisterSchema
from extensions import db, redis_client
from utils.auth import (
    verify_password, generate_password_hash,
    check_login_attempts, record_login_attempt,
    revoke_token, is_token_revoked
)
from utils.responses import success_response, error_response, validation_error_response
from utils.decorators import rate_limit
from utils.captcha import generate_captcha_image, verify_captcha
from marshmallow import ValidationError

# 创建命名空间
auth_ns = Namespace('auth', description='用户认证相关操作')

# 定义数据模型
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
    'remember_me': fields.Boolean(default=False, description='记住我')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱地址'),
    'password': fields.String(required=True, description='密码'),
    'confirm_password': fields.String(required=True, description='确认密码'),
    'phone': fields.String(required=True, description='手机号'),
    'real_name': fields.String(required=True, description='真实姓名'),
    'student_id': fields.String(required=True, description='学生号'),
    'captcha': fields.String(required=True, description='验证码')
})

check_field_model = auth_ns.model('CheckField', {
    'value': fields.String(required=True, description='值')
})

password_change_model = auth_ns.model('PasswordChange', {
    'old_password': fields.String(required=True, description='旧密码'),
    'new_password': fields.String(required=True, description='新密码'),
    'confirm_password': fields.String(required=True, description='确认密码')
})

password_reset_model = auth_ns.model('PasswordReset', {
    'email': fields.String(required=True, description='邮箱地址')
})

refresh_token_model = auth_ns.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description='刷新令牌')
})

@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('user_login')
    @rate_limit("5/minute")  # 限流：每分钟5次
    def post(self):
        """用户登录"""
        try:
            schema = UserLoginSchema()
            data = schema.load(request.json)

            # 获取用户
            user = User.query.filter(
                (User.username == data['username']) |
                (User.email == data['username'])
            ).first()

            if not user:
                # 记录登录失败
                AuditLog.log_login(None, data['username'], False, "用户不存在")
                return error_response("用户名或密码错误", 401)

            # 检查登录限制
            if not user.can_login():
                if user.is_locked():
                    return error_response("账户已被锁定，请稍后再试", 423)
                return error_response("账户状态异常", 403)

            # 验证密码
            if not verify_password(data['password'], user.password_hash):
                user.record_failed_login()
                AuditLog.log_login(user.id, user.username, False, "密码错误")
                return error_response("用户名或密码错误", 401)

            # 检查登录尝试限制
            if not check_login_attempts(user.username):
                return error_response("登录尝试次数过多，请稍后再试", 429)

            # 生成JWT令牌
            additional_claims = {
                'role': user.role.value,
                'permissions': user.get_permissions() if hasattr(user, 'admin_profile') and user.admin_profile else []
            }

            expires_delta = timedelta(days=30) if data.get('remember_me') else current_app.config['JWT_ACCESS_TOKEN_EXPIRES']

            access_token = create_access_token(
                identity=user.id,
                additional_claims=additional_claims,
                expires_delta=expires_delta
            )
            refresh_token = create_refresh_token(identity=user.id)

            # 更新登录信息
            user.update_login_info(request.remote_addr)

            # 记录成功登录
            AuditLog.log_login(user.id, user.username, True)

            # 清除登录失败计数
            redis_client.delete(f"login_attempts:{user.username}")

            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(expires_delta.total_seconds()),
                'user': UserSchema().dump(user)
            }

            return success_response("登录成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/logout')
class LogoutResource(Resource):
    @jwt_required()
    @auth_ns.doc('user_logout')
    def post(self):
        """用户登出"""
        try:
            current_user_id = get_jwt_identity()
            jti = get_jwt()['jti']

            # 将令牌加入黑名单
            redis_client.set(
                f"revoked_token:{jti}",
                "true",
                ex=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            )

            # 记录登出
            AuditLog.log_action(
                action=AuditAction.LOGOUT,
                user_id=current_user_id,
                description="用户登出"
            )

            return success_response("登出成功")

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/refresh')
class RefreshTokenResource(Resource):
    @jwt_required(refresh=True)
    @auth_ns.expect(refresh_token_model)
    @auth_ns.doc('refresh_token')
    def post(self):
        """刷新访问令牌"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.is_active():
                return error_response("用户不存在或已被禁用", 401)

            # 生成新的访问令牌
            additional_claims = {
                'role': user.role.value,
                'permissions': user.get_permissions() if hasattr(user, 'admin_profile') and user.admin_profile else []
            }

            new_token = create_access_token(
                identity=current_user_id,
                additional_claims=additional_claims
            )

            response_data = {
                'access_token': new_token,
                'token_type': 'Bearer'
            }

            return success_response("令牌刷新成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/change-password')
class ChangePasswordResource(Resource):
    @jwt_required()
    @auth_ns.expect(password_change_model)
    @auth_ns.doc('change_password')
    def post(self):
        """修改密码"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            schema = UserPasswordChangeSchema()
            data = schema.load(request.json)

            # 验证旧密码
            if not verify_password(data['old_password'], user.password_hash):
                AuditLog.log_action(
                    action=AuditAction.PASSWORD_CHANGE,
                    user_id=current_user_id,
                    success=False,
                    description="旧密码错误"
                )
                return error_response("旧密码错误", 400)

            # 更新密码
            user.password_hash = generate_password_hash(data['new_password'])
            user.save()

            # 记录密码修改
            AuditLog.log_action(
                action=AuditAction.PASSWORD_CHANGE,
                user_id=current_user_id,
                description="用户修改密码"
            )

            return success_response("密码修改成功")

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/reset-password')
class ResetPasswordResource(Resource):
    @auth_ns.expect(password_reset_model)
    @auth_ns.doc('reset_password')
    @rate_limit("3/minute")  # 限流：每分钟3次
    def post(self):
        """重置密码"""
        try:
            schema = UserPasswordResetSchema()
            data = schema.load(request.json)

            # 查找用户
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                # 为了安全，即使邮箱不存在也返回成功
                return success_response("如果邮箱存在，重置链接已发送")

            # 生成重置令牌
            reset_token = str(uuid.uuid4())
            reset_token_key = f"reset_token:{reset_token}"

            # 存储重置令牌（24小时有效）
            redis_client.setex(
                reset_token_key,
                86400,  # 24小时
                user.id
            )

            # 发送重置邮件
            try:
                from flask_mail import Message as MailMessage
                mail = current_app.extensions.get('mail')
                if mail:
                    reset_url = f"{request.host_url}reset-password?token={reset_token}"

                    mail_message = MailMessage(
                        subject='密码重置请求',
                        sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                        recipients=[user.email],
                        body=f'''
请点击以下链接重置您的密码：
{reset_url}

如果您没有请求重置密码，请忽略此邮件。
此链接将在24小时后失效。
                    '''
                    )
                    mail.send(mail_message)

            except Exception as e:
                current_app.logger.error(f"发送重置邮件失败: {str(e)}")

            # 记录密码重置请求
            AuditLog.log_action(
                action=AuditAction.PASSWORD_CHANGE,
                user_id=user.id,
                description="请求密码重置"
            )

            return success_response("如果邮箱存在，重置链接已发送")

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/verify-reset-token/<token>')
class VerifyResetTokenResource(Resource):
    @auth_ns.doc('verify_reset_token')
    def get(self, token):
        """验证重置令牌"""
        try:
            reset_token_key = f"reset_token:{token}"
            user_id = redis_client.get(reset_token_key)

            if not user_id:
                return error_response("重置令牌无效或已过期", 400)

            user = User.query.get(user_id.decode())
            if not user:
                return error_response("用户不存在", 404)

            return success_response("重置令牌有效", {
                'user_id': user.id,
                'username': user.username
            })

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/confirm-reset-password/<token>')
class ConfirmResetPasswordResource(Resource):
    @auth_ns.doc('confirm_reset_password')
    def post(self, token):
        """确认重置密码"""
        try:
            reset_token_key = f"reset_token:{token}"
            user_id = redis_client.get(reset_token_key)

            if not user_id:
                return error_response("重置令牌无效或已过期", 400)

            data = request.json
            new_password = data.get('new_password')

            if not new_password or len(new_password) < 6:
                return error_response("密码长度至少6位", 400)

            user = User.query.get(user_id.decode())
            if not user:
                return error_response("用户不存在", 404)

            # 更新密码
            user.password_hash = generate_password_hash(new_password)
            user.save()

            # 删除重置令牌
            redis_client.delete(reset_token_key)

            # 记录密码重置
            AuditLog.log_action(
                action=AuditAction.PASSWORD_CHANGE,
                user_id=user.id,
                description="通过邮件重置密码"
            )

            return success_response("密码重置成功")

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/current-user')
class CurrentUserResource(Resource):
    @jwt_required()
    @auth_ns.doc('get_current_user')
    def get(self):
        """获取当前用户信息"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            user_data = UserSchema().dump(user)

            # 添加权限信息
            user_data['permissions'] = user.get_permissions() if hasattr(user, 'admin_profile') and user.admin_profile else []

            return success_response("获取用户信息成功", user_data)

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/check-token')
class CheckTokenResource(Resource):
    @jwt_required()
    @auth_ns.doc('check_token')
    def get(self):
        """检查令牌有效性"""
        try:
            jti = get_jwt()['jti']

            if is_token_revoked(jti):
                return error_response("令牌已失效", 401)

            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.is_active():
                return error_response("用户不存在或已被禁用", 401)

            return success_response("令牌有效", {
                'user_id': user.id,
                'username': user.username,
                'role': user.role.value
            })

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/register')
class RegisterResource(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.doc('user_register')
    @rate_limit("3/minute")  # 限流：每分钟3次
    def post(self):
        """用户注册"""
        try:
            # 验证数据
            schema = UserRegisterSchema()
            data = schema.load(request.json)

            # 验证验证码
            captcha_id = request.json.get('captcha_id')
            if not captcha_id or not verify_captcha(captcha_id, data['captcha'], redis_client):
                return error_response("验证码错误", 400)

            # 检查注册限制
            registration_key = f"registration:{request.remote_addr}"
            registration_count = redis_client.get(registration_key)
            if registration_count and int(registration_count) >= 3:
                return error_response("注册次数过多，请稍后再试", 429)

            # 创建用户
            user = User(
                username=data['username'],
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                role=UserRole.STUDENT  # 默认注册为学生角色
            )

            # 创建用户资料
            from models import UserProfile
            user_profile = UserProfile(
                user=user,
                first_name=data['real_name'],
                last_name="",  # 暂时为空，可以后续完善
                phone=data['phone']
            )

            # 如果是学生角色，创建学生记录
            from models import Student
            student = Student(
                user=user,
                student_id=data['student_id'],
                first_name=data['real_name'],
                last_name=""
            )

            # 保存到数据库
            db.session.add(user)
            db.session.add(user_profile)
            db.session.add(student)
            db.session.commit()

            # 记录注册日志
            AuditLog.log_action(
                action=AuditAction.USER_CREATED,
                user_id=user.id,
                description="用户注册"
            )

            # 更新注册计数
            redis_client.setex(registration_key, 3600, (int(registration_count or 0) + 1))

            # 删除已使用的验证码
            redis_client.delete(f"captcha:{captcha_id}")

            return success_response("注册成功", {
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            })

        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@auth_ns.route('/captcha')
class CaptchaResource(Resource):
    @auth_ns.doc('get_captcha')
    def get(self):
        """获取验证码"""
        try:
            # 生成验证码
            captcha_data = generate_captcha_image()

            # 存储验证码到Redis（5分钟有效）
            captcha_id = store_captcha(captcha_data, redis_client, expire_time=300)

            return success_response("验证码生成成功", {
                'captcha_id': captcha_id,
                'captcha_image': captcha_data['captcha_image']
            })

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/check-username')
class CheckUsernameResource(Resource):
    @auth_ns.expect(check_field_model)
    @auth_ns.doc('check_username')
    def post(self):
        """检查用户名是否可用"""
        try:
            data = request.json
            username = data.get('value', '').strip()

            if not username:
                return error_response("用户名不能为空", 400)

            if len(username) < 3:
                return error_response("用户名长度至少为3位", 400)

            if User.query.filter_by(username=username).first():
                return error_response("用户名已存在", 409)

            return success_response("用户名可用")

        except Exception as e:
            return error_response(str(e), 500)

@auth_ns.route('/check-email')
class CheckEmailResource(Resource):
    @auth_ns.expect(check_field_model)
    @auth_ns.doc('check_email')
    def post(self):
        """检查邮箱是否可用"""
        try:
            data = request.json
            email = data.get('value', '').strip()

            if not email:
                return error_response("邮箱不能为空", 400)

            if User.query.filter_by(email=email).first():
                return error_response("邮箱已被注册", 409)

            return success_response("邮箱可用")

        except Exception as e:
            return error_response(str(e), 500)