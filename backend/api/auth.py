# ========================================
# 学生信息管理系统 - 认证API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields, validate
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import uuid
import os

from models import User, UserRole, AuditLog, AuditAction, UserProfile
from schemas import UserSchema, UserLoginSchema, UserPasswordChangeSchema, UserPasswordResetSchema, UserRegisterSchema, UserUpdateSchema
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

# 个人信息相关数据模型
profile_update_model = auth_ns.model('ProfileUpdate', {
    'first_name': fields.String(description='姓', validate=validate.Length(min=1, max=50)),
    'last_name': fields.String(description='名', validate=validate.Length(min=1, max=50)),
    'phone': fields.String(description='手机号码', validate=validate.Regexp(r'^1[3-9]\d{9}$')),
    'gender': fields.String(description='性别', enum=['male', 'female', 'other']),
    'birthday': fields.Date(description='生日'),
    'address': fields.String(description='地址'),
    'city': fields.String(description='城市'),
    'province': fields.String(description='省份'),
    'postal_code': fields.String(description='邮政编码'),
    'department': fields.String(description='部门'),
    'major': fields.String(description='专业'),
    'degree': fields.String(description='学位')
})

avatar_upload_model = auth_ns.model('AvatarUpload', {
    'avatar': fields.String(required=True, description='头像Base64数据')
})

@auth_ns.route('/profile')
class UserProfileResource(Resource):
    @jwt_required()
    @auth_ns.doc('get_user_profile')
    def get(self):
        """获取当前用户个人信息"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            # 序列化用户信息
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return success_response("获取个人信息成功", user_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @auth_ns.expect(profile_update_model)
    @auth_ns.doc('update_user_profile')
    def put(self):
        """更新当前用户个人信息"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            schema = UserUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新用户资料
            if not user.profile:
                # 如果用户资料不存在，创建新的
                profile_data = {
                    'user_id': user.id,
                    'first_name': data.get('first_name', user.username),
                    'last_name': data.get('last_name', ''),
                }
                profile = UserProfile(**{k: v for k, v in profile_data.items() if v is not None})
                profile.save()
                user.profile = profile
            else:
                # 更新现有资料
                profile_fields = [
                    'first_name', 'last_name', 'phone', 'gender', 'birthday',
                    'address', 'city', 'province', 'postal_code',
                    'department', 'major', 'degree'
                ]

                for field in profile_fields:
                    if data.get(field) is not None:
                        old_value = getattr(user.profile, field)
                        new_value = data[field]
                        if old_value != new_value:
                            old_values[f'profile_{field}'] = old_value
                            setattr(user.profile, field, new_value)
                            new_values[f'profile_{field}'] = new_value

            # 更新邮箱（如果提供）
            if data.get('email') and data['email'] != user.email:
                # 检查邮箱唯一性
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user.id:
                    return error_response("邮箱已被其他用户使用", 400)

                old_values['email'] = user.email
                user.email = data['email']
                new_values['email'] = data['email']

            # 保存更改
            user.save()
            if user.profile:
                user.profile.save()

            # 记录审计日志
            if old_values or new_values:
                AuditLog.log_update(
                    user_id=current_user_id,
                    resource_type='user_profile',
                    resource_id=user.id,
                    resource_name=user.username,
                    old_values=old_values if old_values else None,
                    new_values=new_values if new_values else None
                )

            # 返回更新后的用户信息
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return success_response("个人信息更新成功", user_data)

        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@auth_ns.route('/avatar')
class UserAvatarResource(Resource):
    @jwt_required()
    @auth_ns.expect(avatar_upload_model)
    @auth_ns.doc('upload_avatar')
    @rate_limit("5/minute")  # 限制上传频率
    def post(self):
        """上传用户头像"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            data = request.get_json()
            if not data or 'avatar' not in data:
                return error_response("请提供头像数据", 400)

            avatar_data = data['avatar']

            # 验证Base64数据
            import base64
            import re
            from datetime import datetime

            # 检查数据格式
            if not re.match(r'^data:image/(png|jpg|jpeg);base64,', avatar_data):
                return error_response("头像格式不正确，请上传PNG或JPG格式图片", 400)

            # 解码Base64数据
            try:
                # 提取Base64部分
                base64_data = avatar_data.split(',')[1]
                image_bytes = base64.b64decode(base64_data)

                # 检查文件大小（限制2MB）
                if len(image_bytes) > 2 * 1024 * 1024:
                    return error_response("头像文件大小不能超过2MB", 400)

                # 生成文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"avatar_{user.id}_{timestamp}.jpg"

                # 保存到uploads目录
                upload_dir = os.path.join(current_app.root_path, 'uploads', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)

                filepath = os.path.join(upload_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)

                # 删除旧头像
                if user.profile and user.profile.avatar:
                    old_avatar_path = os.path.join(current_app.root_path, user.profile.avatar.lstrip('/'))
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)

                # 更新用户头像路径
                if not user.profile:
                    user.profile = UserProfile(user_id=user.id)

                user.profile.avatar = f"/uploads/avatars/{filename}"
                user.profile.save()

                # 记录审计日志
                AuditLog.log_update(
                    user_id=current_user_id,
                    resource_type='user_avatar',
                    resource_id=user.id,
                    resource_name=user.username,
                    old_values={'avatar': 'updated'},
                    new_values={'avatar': user.profile.avatar}
                )

                return success_response("头像上传成功", {
                    'avatar_url': user.profile.avatar
                })

            except Exception as decode_error:
                return error_response("头像数据解码失败", 400)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @auth_ns.doc('delete_avatar')
    def delete(self):
        """删除用户头像"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return error_response("用户不存在", 404)

            if not user.profile or not user.profile.avatar:
                return error_response("用户没有头像", 400)

            # 删除头像文件
            avatar_path = os.path.join(current_app.root_path, user.profile.avatar.lstrip('/'))
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

            # 更新数据库
            old_avatar = user.profile.avatar
            user.profile.avatar = None
            user.profile.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='user_avatar',
                resource_id=user.id,
                resource_name=user.username,
                old_values={'avatar': old_avatar},
                new_values={'avatar': None}
            )

            return success_response("头像删除成功")

        except Exception as e:
            return error_response(str(e), 500)