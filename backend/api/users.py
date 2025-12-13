# ========================================
# 学生信息管理系统 - 用户管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime

from models import User, UserProfile, UserRole, UserStatus, AuditLog, AuditAction
from schemas import (
    UserSchema, UserCreateSchema, UserUpdateSchema,
    UserSearchSchema, UserListSchema
)
from extensions import db
from utils.auth import generate_password_hash, verify_password
from utils.responses import (
    success_response, error_response, validation_error_response,
    not_found_response, forbidden_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query

# 创建命名空间
users_ns = Namespace('users', description='用户管理相关操作')

# 定义数据模型
user_create_model = users_ns.model('UserCreate', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    'confirm_password': fields.String(required=True, description='确认密码'),
    'role': fields.String(required=True, description='角色', enum=['admin', 'teacher', 'student']),
    'first_name': fields.String(required=True, description='姓'),
    'last_name': fields.String(required=True, description='名'),
    'phone': fields.String(description='手机号码'),
    'gender': fields.String(description='性别', enum=['male', 'female', 'other']),
    'birthday': fields.Date(description='生日'),
    'department': fields.String(description='部门'),
    'major': fields.String(description='专业'),
    'status': fields.String(description='状态', enum=['active', 'inactive', 'suspended'])
})

user_update_model = users_ns.model('UserUpdate', {
    'email': fields.String(description='邮箱'),
    'role': fields.String(description='角色', enum=['admin', 'teacher', 'student']),
    'status': fields.String(description='状态', enum=['active', 'inactive', 'suspended']),
    'first_name': fields.String(description='姓'),
    'last_name': fields.String(description='名'),
    'phone': fields.String(description='手机号码'),
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

user_search_model = users_ns.model('UserSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'role': fields.String(description='角色筛选'),
    'status': fields.String(description='状态筛选'),
    'department': fields.String(description='部门筛选'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='created_at'),
    'sort_order': fields.String(description='排序方式', default='desc')
})

@users_ns.route('')
class UserListResource(Resource):
    @jwt_required()
    @users_ns.doc('list_users')
    @users_ns.expect(user_search_model)
    @require_permission('user_management')
    def get(self):
        """获取用户列表"""
        try:
            schema = UserSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = User.query

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.join(UserProfile).filter(
                    or_(
                        User.username.like(keyword),
                        User.email.like(keyword),
                        UserProfile.first_name.like(keyword),
                        UserProfile.last_name.like(keyword),
                        UserProfile.phone.like(keyword)
                    )
                )
            else:
                query = query.join(UserProfile)

            # 角色筛选
            if data.get('role'):
                query = query.filter(User.role == UserRole(data['role']))

            # 状态筛选
            if data.get('status'):
                query = query.filter(User.status == UserStatus(data['status']))

            # 部门筛选
            if data.get('department'):
                query = query.filter(UserProfile.department.like(f"%{data['department']}%"))

            # 排序
            sort_field = getattr(User, data['sort_by'], User.created_at)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            users = pagination.items

            # 序列化
            user_schema = UserSchema(many=True)
            user_data = user_schema.dump(users)

            response_data = {
                'users': user_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取用户列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @users_ns.expect(user_create_model)
    @users_ns.doc('create_user')
    @require_permission('user_management')
    @rate_limit("10/minute")
    def post(self):
        """创建用户"""
        try:
            schema = UserCreateSchema()
            data = schema.load(request.json)

            # 检查用户名和邮箱唯一性
            if User.query.filter_by(username=data['username']).first():
                return error_response("用户名已存在", 400)

            if User.query.filter_by(email=data['email']).first():
                return error_response("邮箱已存在", 400)

            # 创建用户
            user = User(
                username=data['username'],
                email=data['email'],
                role=UserRole(data['role']),
                status=UserStatus(data.get('status', 'active'))
            )
            user.password_hash = generate_password_hash(data['password'])
            user.save()

            # 创建用户资料
            profile = UserProfile(
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                gender=data.get('gender'),
                birthday=data.get('birthday'),
                department=data.get('department'),
                major=data.get('major')
            )
            profile.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=f"{data['first_name']} {data['last_name']} ({data['username']})"
            )

            # 返回用户信息
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return success_response("用户创建成功", user_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@users_ns.route('/<string:user_id>')
class UserResource(Resource):
    @jwt_required()
    @users_ns.doc('get_user')
    def get(self, user_id):
        """获取用户详情"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            # 检查权限：用户本人或有user_management权限
            current_user_id = get_jwt_identity()
            if current_user_id != user_id and not g.current_user.has_permission('user_management'):
                return forbidden_response("权限不足")

            # 序列化
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            # 如果是本人或管理员，显示更多信息
            if current_user_id == user_id or g.current_user.has_permission('user_management'):
                user_data['email'] = user.email
                if user.profile:
                    user_data['profile']['phone'] = user.profile.phone

            return success_response("获取用户信息成功", user_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @users_ns.expect(user_update_model)
    @users_ns.doc('update_user')
    def put(self, user_id):
        """更新用户信息"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            if current_user_id != user_id and not g.current_user.has_permission('user_management'):
                return forbidden_response("权限不足")

            schema = UserUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新用户基本信息
            if data.get('email') and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return error_response("邮箱已被其他用户使用", 400)
                old_values['email'] = user.email
                user.email = data['email']
                new_values['email'] = data['email']

            if data.get('role') and g.current_user.has_permission('user_management'):
                old_role = user.role.value
                user.role = UserRole(data['role'])
                new_values['role'] = data['role']

            if data.get('status') and g.current_user.has_permission('user_management'):
                old_status = user.status.value
                user.status = UserStatus(data['status'])
                new_values['status'] = data['status']

            # 更新密码
            if data.get('password'):
                if not verify_password(data.get('old_password'), user.password_hash):
                    return error_response("旧密码错误", 400)
                user.password_hash = generate_password_hash(data['password'])
                new_values['password'] = 'updated'

            # 更新用户资料
            profile_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'phone': data.get('phone'),
                'gender': data.get('gender'),
                'birthday': data.get('birthday'),
                'address': data.get('address'),
                'city': data.get('city'),
                'province': data.get('province'),
                'postal_code': data.get('postal_code'),
                'department': data.get('department'),
                'major': data.get('major'),
                'degree': data.get('degree')
            }

            if user.profile:
                for key, value in profile_data.items():
                    if value is not None:
                        old_value = getattr(user.profile, key)
                        if old_value != value:
                            old_values[f'profile_{key}'] = old_value
                            setattr(user.profile, key, value)
                            new_values[f'profile_{key}'] = value
            else:
                profile = UserProfile(user_id=user.id, **{k: v for k, v in profile_data.items() if v is not None})
                profile.save()

            user.save()
            if user.profile:
                user.profile.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username,
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的用户信息
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return success_response("用户信息更新成功", user_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @jwt_required()
    @users_ns.doc('delete_user')
    @require_permission('user_management')
    def delete(self, user_id):
        """删除用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            # 检查是否可以删除（例如，是否有相关数据）
            if hasattr(user, 'student_record') and user.student_record:
                # 检查是否有选课记录、成绩等
                if user.student_record.enrollments:
                    return error_response("该学生有选课记录，无法删除", 400)

            if hasattr(user, 'teacher_record') and user.teacher_record:
                # 检查是否有授课课程
                if user.teacher_record.courses:
                    return error_response("该教师有授课课程，无法删除", 400)

            # 记录审计日志
            AuditLog.log_delete(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username
            )

            # 删除用户（级联删除相关数据）
            db.session.delete(user)
            db.session.commit()

            return success_response("用户删除成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@users_ns.route('/<string:user_id>/activate')
class UserActivateResource(Resource):
    @jwt_required()
    @users_ns.doc('activate_user')
    @require_permission('user_management')
    def post(self, user_id):
        """激活用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            if user.is_active():
                return error_response("用户已激活", 400)

            user.status = UserStatus.ACTIVE
            user.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username,
                old_values={'status': user.status.value},
                new_values={'status': 'active'}
            )

            return success_response("用户激活成功")

        except Exception as e:
            return error_response(str(e), 500)

@users_ns.route('/<string:user_id>/deactivate')
class UserDeactivateResource(Resource):
    @jwt_required()
    @users_ns.doc('deactivate_user')
    @require_permission('user_management')
    def post(self, user_id):
        """停用用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            if not user.is_active():
                return error_response("用户已停用", 400)

            # 检查是否可以停用当前用户
            if user_id == get_jwt_identity():
                return error_response("不能停用自己的账户", 400)

            user.status = UserStatus.INACTIVE
            user.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username,
                old_values={'status': user.status.value},
                new_values={'status': 'inactive'}
            )

            return success_response("用户停用成功")

        except Exception as e:
            return error_response(str(e), 500)

@users_ns.route('/<string:user_id>/lock')
class UserLockResource(Resource):
    @jwt_required()
    @users_ns.doc('lock_user')
    @require_permission('user_management')
    def post(self, user_id):
        """锁定用户"""
        try:
            from datetime import datetime, timedelta

            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            # 锁定30分钟
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            user.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username,
                old_values={'locked_until': None},
                new_values={'locked_until': user.locked_until.isoformat()}
            )

            return success_response("用户锁定成功")

        except Exception as e:
            return error_response(str(e), 500)

@users_ns.route('/<string:user_id>/unlock')
class UserUnlockResource(Resource):
    @jwt_required()
    @users_ns.doc('unlock_user')
    @require_permission('user_management')
    def post(self, user_id):
        """解锁用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return not_found_response("用户不存在")

            user.locked_until = None
            user.failed_login_attempts = 0
            user.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='user',
                resource_id=user.id,
                resource_name=user.username,
                old_values={'locked_until': 'locked'},
                new_values={'locked_until': None}
            )

            return success_response("用户解锁成功")

        except Exception as e:
            return error_response(str(e), 500)

@users_ns.route('/stats')
class UserStatsResource(Resource):
    @jwt_required()
    @users_ns.doc('get_user_stats')
    @require_permission('user_management')
    def get(self):
        """获取用户统计信息"""
        try:
            stats = {}

            # 总用户数
            stats['total_users'] = User.query.count()

            # 按角色统计
            stats['users_by_role'] = {
                'admin': User.query.filter_by(role=UserRole.ADMIN).count(),
                'teacher': User.query.filter_by(role=UserRole.TEACHER).count(),
                'student': User.query.filter_by(role=UserRole.STUDENT).count()
            }

            # 按状态统计
            stats['users_by_status'] = {
                'active': User.query.filter_by(status=UserStatus.ACTIVE).count(),
                'inactive': User.query.filter_by(status=UserStatus.INACTIVE).count(),
                'suspended': User.query.filter_by(status=UserStatus.SUSPENDED).count()
            }

            # 按部门统计
            stats['users_by_department'] = db.session.query(
                UserProfile.department, db.func.count(User.id)
            ).join(User).filter(
                UserProfile.department.isnot(None)
            ).group_by(UserProfile.department).all()

            stats['users_by_department'] = dict(stats['users_by_department'])

            # 最近注册用户
            recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
            user_schema = UserSchema(many=True, only=('id', 'username', 'role', 'status', 'created_at'))
            stats['recent_users'] = user_schema.dump(recent_users)

            return success_response("获取用户统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)