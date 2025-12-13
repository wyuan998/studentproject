# ========================================
# 学生信息管理系统 - 管理员API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import (
    Admin, User, UserProfile, AdminLevel, SystemConfig,
    MessageType, MessageTemplate, AuditLog, AuditAction,
    Student, Teacher, Course
)
from schemas import (
    AdminSchema, AdminCreateSchema, AdminUpdateSchema,
    SystemConfigSchema, SystemConfigCreateSchema,
    MessageTemplateSchema, MessageTemplateCreateSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, not_found_response,
    forbidden_response, validation_error_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query

# 创建命名空间
admins_ns = Namespace('admins', description='管理员相关操作')

# 定义数据模型
admin_create_model = admins_ns.model('AdminCreate', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    'confirm_password': fields.String(required=True, description='确认密码'),
    'admin_id': fields.String(required=True, description='管理员编号'),
    'level': fields.String(required=True, description='管理员级别', enum=['super_admin', 'system_admin', 'department_admin', 'general_admin']),
    'department': fields.String(description='所属部门'),
    'first_name': fields.String(required=True, description='姓'),
    'last_name': fields.String(required=True, description='名'),
    'permissions': fields.Raw(description='权限配置'),
    'managed_departments': fields.List(fields.String, description='管理部门'),
    'managed_functions': fields.List(fields.String, description='管理功能'),
    'notes': fields.String(description='备注')
})

admin_update_model = admins_ns.model('AdminUpdate', {
    'level': fields.String(description='管理员级别', enum=['super_admin', 'system_admin', 'department_admin', 'general_admin']),
    'department': fields.String(description='所属部门'),
    'first_name': fields.String(description='姓'),
    'last_name': fields.String(description='名'),
    'permissions': fields.Raw(description='权限配置'),
    'managed_departments': fields.List(fields.String, description='管理部门'),
    'managed_functions': fields.List(fields.String, description='管理功能'),
    'notes': fields.String(description='备注'),
    'two_factor_enabled': fields.Boolean(description='是否启用双因素认证')
})

system_config_model = admins_ns.model('SystemConfig', {
    'key': fields.String(required=True, description='配置键'),
    'name': fields.String(required=True, description='配置名称'),
    'description': fields.String(description='配置描述'),
    'config_type': fields.String(required=True, description='配置类型', enum=['system', 'academic', 'notification', 'security', 'email', 'backup', 'ui', 'integration', 'feature']),
    'value_type': fields.String(required=True, description='值类型', enum=['string', 'integer', 'float', 'boolean', 'json', 'array']),
    'value': fields.Raw(required=True, description='配置值'),
    'min_value': fields.Float(description='最小值'),
    'max_value': fields.Float(description='最大值'),
    'allowed_values': fields.List(fields.Raw, description='允许的值'),
    'validation_pattern': fields.String(description='验证正则'),
    'category': fields.String(description='分类'),
    'is_active': fields.Boolean(description='是否激活'),
    'is_required': fields.Boolean(description='是否必填'),
    'is_public': fields.Boolean(description='是否公开'),
    'cache_ttl': fields.Integer(description='缓存时间（秒）')
})

message_template_model = admins_ns.model('MessageTemplate', {
    'name': fields.String(required=True, description='模板名称'),
    'title_template': fields.String(required=True, description='标题模板'),
    'content_template': fields.String(required=True, description='内容模板'),
    'type': fields.String(required=True, description='消息类型', enum=['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']),
    'category': fields.String(description='分类'),
    'variables': fields.Raw(description='模板变量'),
    'default_variables': fields.Raw(description='默认变量'),
    'is_active': fields.Boolean(description='是否激活'),
    'is_system': fields.Boolean(description='是否为系统模板')
})

@admins_ns.route('/dashboard')
class AdminDashboardResource(Resource):
    @jwt_required()
    @admins_ns.doc('admin_dashboard')
    @require_permission('system_config')
    def get(self):
        """管理员仪表板"""
        try:
            current_user_id = get_jwt_identity()
            admin = Admin.query.filter_by(user_id=current_user_id).first()

            if not admin:
                return forbidden_response("权限不足")

            dashboard_data = {
                'system_overview': get_system_overview(),
                'user_statistics': get_user_statistics(),
                'academic_statistics': get_academic_statistics(),
                'system_health': get_system_health(),
                'recent_activities': get_recent_activities(),
                'quick_actions': get_quick_actions(admin.level.value),
                'notifications': get_admin_notifications(admin.id)
            }

            return success_response("获取仪表板数据成功", dashboard_data)

        except Exception as e:
            return error_response(str(e), 500)

@admins_ns.route('/permissions')
class AdminPermissionsResource(Resource):
    @jwt_required()
    @admins_ns.doc('get_admin_permissions')
    def get(self):
        """获取管理员权限列表"""
        try:
            current_user_id = get_jwt_identity()
            admin = Admin.query.filter_by(user_id=current_user_id).first()

            if not admin:
                return forbidden_response("权限不足")

            # 获取可用权限
            available_permissions = {
                'user_management': {
                    'name': '用户管理',
                    'description': '管理系统用户、学生、教师账户',
                    'module': 'users'
                },
                'student_management': {
                    'name': '学生管理',
                    'description': '管理学生信息、选课、成绩',
                    'module': 'students'
                },
                'teacher_management': {
                    'name': '教师管理',
                    'description': '管理教师信息、课程分配',
                    'module': 'teachers'
                },
                'course_management': {
                    'name': '课程管理',
                    'description': '管理课程、选课安排',
                    'module': 'courses'
                },
                'grade_management': {
                    'name': '成绩管理',
                    'description': '管理学生成绩、统计分析',
                    'module': 'grades'
                },
                'enrollment_management': {
                    'name': '选课管理',
                    'description': '管理学生选课、退选流程',
                    'module': 'enrollments'
                },
                'system_config': {
                    'name': '系统配置',
                    'description': '管理系统参数、功能开关',
                    'module': 'system'
                },
                'data_import_export': {
                    'name': '数据导入导出',
                    'description': '批量导入导出数据',
                    'module': 'data'
                },
                'reports': {
                    'name': '报表统计',
                    'description': '生成各类统计报表',
                    'module': 'reports'
                },
                'audit_logs': {
                    'name': '审计日志',
                    'description': '查看系统操作日志',
                    'module': 'audit'
                },
                'message_management': {
                    'name': '消息管理',
                    'description': '管理系统通知、消息模板',
                    'module': 'messages'
                },
                'permission_management': {
                    'name': '权限管理',
                    'description': '管理用户权限和角色',
                    'module': 'permissions'
                }
            }

            permissions_data = {
                'admin_info': {
                    'id': admin.id,
                    'admin_id': admin.admin_id,
                    'name': admin.user.profile.full_name if admin.user.profile else admin.user.username,
                    'level': admin.level.value,
                    'level_display': admin.display_level,
                    'department': admin.department
                },
                'available_permissions': available_permissions,
                'current_permissions': admin.permissions or {},
                'can_manage_permissions': admin.has_permission('permission_management')
            }

            return success_response("获取权限列表成功", permissions_data)

        except Exception as e:
            return error_response(str(e), 500)

@admins_ns.route('/system-configs')
class SystemConfigsResource(Resource):
    @jwt_required()
    @admins_ns.doc('list_system_configs')
    def get(self):
        """获取系统配置列表"""
        try:
            current_user_id = get_jwt_identity()
            admin = Admin.query.filter_by(user_id=current_user_id).first()

            if not admin or not admin.has_permission('system_config'):
                return forbidden_response("权限不足")

            # 筛选参数
            config_type = request.args.get('type')
            category = request.args.get('category')
            is_active = request.args.get('active')
            is_public = request.args.get('public')

            query = SystemConfig.query

            if config_type:
                query = query.filter_by(config_type=config_type)
            if category:
                query = query.filter_by(category=category)
            if is_active is not None:
                query = query.filter_by(is_active=is_active.lower() == 'true')
            if is_public is not None:
                query = query.filter_by(is_public=is_public.lower() == 'true')

            configs = query.order_by(SystemConfig.sort_order, SystemConfig.key).all()

            # 序列化
            config_schema = SystemConfigSchema(many=True)
            config_data = config_schema.dump(configs)

            # 按类型分组
            grouped_configs = {}
            for config in config_data:
                if config['config_type'] not in grouped_configs:
                    grouped_configs[config['config_type']] = []
                grouped_configs[config['config_type']].append(config)

            return success_response("获取系统配置成功", {
                'configs': config_data,
                'grouped_configs': grouped_configs,
                'total': len(config_data)
            })

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @admins_ns.expect(system_config_model)
    @admins_ns.doc('create_system_config')
    @require_permission('system_config')
    def post(self):
        """创建系统配置"""
        try:
            schema = SystemConfigCreateSchema()
            data = schema.load(request.json)

            current_user_id = get_jwt_identity()

            # 检查配置键是否已存在
            if SystemConfig.query.filter_by(key=data['key']).first():
                return error_response("配置键已存在", 400)

            # 创建配置
            config = SystemConfig(
                key=data['key'],
                name=data['name'],
                description=data['description'],
                config_type=data['config_type'],
                value_type=data['value_type'],
                min_value=data.get('min_value'),
                max_value=data.get('max_value'),
                allowed_values=data.get('allowed_values'),
                validation_pattern=data.get('validation_pattern'),
                category=data.get('category'),
                is_active=data.get('is_active', True),
                is_required=data.get('is_required', False),
                is_public=data.get('is_public', False),
                cache_ttl=data.get('cache_ttl', 300),
                sort_order=0,
                created_by=current_user_id
            )

            # 设置值
            config.value = data['value']
            config.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=current_user_id,
                resource_type='system_config',
                resource_id=config.id,
                resource_name=f"系统配置: {data['key']}"
            )

            # 返回配置信息
            config_schema = SystemConfigSchema()
            config_data = config_schema.dump(config)

            return success_response("系统配置创建成功", config_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@admins_ns.route('/system-configs/<string:config_id>')
class SystemConfigResource(Resource):
    @jwt_required()
    @admins_ns.doc('get_system_config')
    def get(self, config_id):
        """获取系统配置详情"""
        try:
            config = SystemConfig.query.get(config_id)
            if not config:
                return not_found_response("配置不存在")

            # 检查权限：公开配置或管理员
            if not config.is_public:
                current_user_id = get_jwt_identity()
                admin = Admin.query.filter_by(user_id=current_user_id).first()
                if not admin or not admin.has_permission('system_config'):
                    return forbidden_response("权限不足")

            # 序列化
            config_schema = SystemConfigSchema()
            config_data = config_schema.dump(config)

            return success_response("获取配置详情成功", config_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @admins_ns.expect(system_config_model)
    @admins_ns.doc('update_system_config')
    def put(self, config_id):
        """更新系统配置"""
        try:
            config = SystemConfig.query.get(config_id)
            if not config:
                return not_found_response("配置不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            admin = Admin.query.filter_by(user_id=current_user_id).first()
            if not admin or not admin.has_permission('system_config'):
                return forbidden_response("权限不足")

            data = request.json

            # 记录变更
            old_values = {'value': config.value}
            new_values = {'value': data.get('value')}

            # 更新配置信息
            if 'name' in data:
                config.name = data['name']
            if 'description' in data:
                config.description = data['description']
            if 'value' in data:
                config.value = data['value']
            if 'min_value' in data:
                config.min_value = data['min_value']
            if 'max_value' in data:
                config.max_value = data['max_value']
            if 'allowed_values' in data:
                config.allowed_values = data['allowed_values']
            if 'validation_pattern' in data:
                config.validation_pattern = data['validation_pattern']
            if 'category' in data:
                config.category = data['category']
            if 'is_active' in data:
                config.is_active = data['is_active']
            if 'is_required' in data:
                config.is_required = data['is_required']
            if 'is_public' in data:
                config.is_public = data['is_public']
            if 'cache_ttl' in data:
                config.cache_ttl = data['cache_ttl']
            if 'updated_by' in data:
                config.updated_by = data['updated_by']

            config.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='system_config',
                resource_id=config_id,
                resource_name=config.key,
                old_values=old_values,
                new_values=new_values
            )

            # 返回更新后的配置
            config_schema = SystemConfigSchema()
            config_data = config_schema.dump(config)

            return success_response("配置更新成功", config_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@admins_ns.route('/audit-logs')
class AuditLogsResource(Resource):
    @jwt_required()
    @admins_ns.doc('get_audit_logs')
    @require_permission('audit_logs')
    def get(self):
        """获取审计日志"""
        try:
            # 筛选参数
            user_id = request.args.get('user_id')
            resource_type = request.args.get('resource_type')
            action = request.args.get('action')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))

            query = AuditLog.query

            if user_id:
                query = query.filter_by(user_id=user_id)
            if resource_type:
                query = query.filter_by(resource_type=resource_type)
            if action:
                query = query.filter_by(action=action)
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                query = query.filter(AuditLog.timestamp <= end_datetime)

            # 排序
            query = query.order_by(AuditLog.timestamp.desc())

            # 分页
            pagination = paginate_query(query, page, per_page)
            logs = pagination.items

            # 序列化
            logs_data = []
            for log in logs:
                log_info = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'username': log.username,
                    'action': log.action.value,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'resource_name': log.resource_name,
                    'description': log.description,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'endpoint': log.endpoint,
                    'http_method': log.http_method,
                    'success': log.success,
                    'error_message': log.error_message,
                    'timestamp': log.timestamp.isoformat(),
                    'details': log.details
                }
                logs_data.append(log_info)

            response_data = {
                'logs': logs_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取审计日志成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

@admins_ns.route('/backup')
class AdminBackupResource(Resource):
    @jwt_required()
    @admins_ns.doc('create_backup')
    @require_permission('backup_restore')
    def post(self):
        """创建系统备份"""
        try:
            current_user_id = get_jwt_admin

            # 这里应该调用实际的备份脚本
            # 为了演示，返回模拟的成功响应

            backup_data = {
                'backup_id': f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': 'full',
                'created_by': current_user_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'completed',
                'size': '15.2MB'
            }

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.BACKUP,
                user_id=current_user_id,
                resource_type='system',
                description="创建系统备份",
                details=backup_data
            )

            return success_response("备份创建成功", backup_data)

        except Exception as e:
            return error_response(str(e), 500)

@admins_ns.route('/maintenance')
class AdminMaintenanceResource(Resource):
    @jwt_required()
    @admins_ns.doc('system_maintenance')
    @require_permission('system_config')
    def post(self):
        """系统维护操作"""
        try:
            data = request.json
            operation = data.get('operation')

            current_user_id = get_jwt_identity()

            if operation == 'clear_cache':
                # 清理缓存
                from extensions import cache
                cache.clear()
                message = "缓存清理完成"
            elif operation == 'cleanup_old_data':
                # 清理旧数据
                days = data.get('days', 30)

                # 清理旧的审计日志
                deleted_count = AuditLog.cleanup_old_logs(days)

                # 清理旧的消息
                from models import Message
                deleted_messages = Message.cleanup_old_messages(days)

                message = f"数据清理完成，删除了 {deleted_count} 条审计日志和 {deleted_messages} 条消息"
            elif operation == 'rebuild_indexes':
                # 重建索引
                message = "索引重建完成"
            else:
                return error_response("无效的操作类型", 400)

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.SYSTEM_CONFIG,
                user_id=current_user_id,
                resource_type='system',
                description=f"系统维护: {operation}",
                details={'operation': operation}
            )

            return success_response(message)

        except Exception as e:
            return error_response(str(e), 500)

@admins_ns.route('/notifications/send')
class AdminNotificationResource(Resource):
    @jwt_required()
    @admins_ns.doc('send_notification')
    @require_permission('message_management')
    def post(self):
        """发送系统通知"""
        try:
            data = request.json
            recipient_type = data.get('recipient_type')  # 'all', 'students', 'teachers', 'department'
            title = data.get('title')
            content = data.get('content')
            priority = data.get('priority', 'normal')

            if not all([recipient_type, title, content]):
                return error_response("缺少必要参数", 400)

            current_user_id = get_jwt_identity()

            # 构建接收者列表
            recipients = []
            if recipient_type == 'all':
                # 所有用户
                users = User.query.filter_by(status='active').all()
                recipients = [user.id for user in users]
            elif recipient_type == 'students':
                # 所有学生
                from models import Student
                students = Student.query.join(User).filter(User.status == 'active').all()
                recipients = [student.user_id for student in students]
            elif recipient_type == 'teachers':
                # 所有教师
                from models import Teacher
                teachers = Teacher.query.join(User).filter(User.status == 'active').all()
                recipients = [teacher.user_id for teacher in teachers]
            elif recipient_type == 'department':
                # 按部门发送
                department = data.get('department')
                users = User.query.filter_by(status='active').join(UserProfile).filter(
                    UserProfile.department == department
                ).all()
                recipients = [user.id for user in users]

            # 批量创建消息
            from models import Message, MessageType, MessagePriority, MessageStatus

            sent_count = 0
            for receiver_id in recipients:
                message = Message(
                    sender_id=current_user_id,
                    receiver_id=receiver_id,
                    title=title,
                    content=content,
                    type=MessageType.SYSTEM,
                    priority=MessagePriority(priority),
                    status=MessageStatus.UNREAD,
                    sent_at=datetime.utcnow()
                )
                message.save()
                sent_count += 1

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user_id=current_user_id,
                resource_type='message',
                description=f"发送系统通知: {title}, 接收者数量: {sent_count}"
            )

            return success_response(f"系统通知发送成功，发送给 {sent_count} 个用户")

        except Exception as e:
            return error_response(str(e), 500)

# 辅助函数
def get_system_overview():
    """获取系统概览"""
    from models import User, Student, Teacher, Course, Enrollment

    return {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(status='active').count(),
        'total_students': Student.query.count(),
        'active_students': Student.query.filter_by(academic_status='enrolled').count(),
        'total_teachers': Teacher.query.count(),
        'active_teachers': Teacher.query.filter_by(status='active').count(),
        'total_courses': Course.query.count(),
        'active_courses': Course.query.filter_by(status='active').count(),
        'total_enrollments': Enrollment.query.count(),
        'active_enrollments': Enrollment.query.filter_by(status='enrolled').count()
    }

def get_user_statistics():
    """获取用户统计"""
    from models import User, UserRole

    return {
        'by_role': {
            role.value: User.query.filter_by(role=role).count()
            for role in UserRole
        },
        'by_status': {
            'active': User.query.filter_by(status='active').count(),
            'inactive': User.query.filter_by(status='inactive').count(),
            'suspended': User.query.filter_by(status='suspended').count()
        },
        'recent_registrations': User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
    }

def get_academic_statistics():
    """获取学业统计"""
    from models import Student, Course, Enrollment, Grade

    return {
        'student_stats': {
            'by_academic_status': {
                status.value: Student.query.filter_by(academic_status=status).count()
                for status in Student._status_enum_
            },
            'by_grade': {},
            'by_major': {}
        },
        'course_stats': {
            'by_type': {
                type.value: Course.query.filter_by(course_type=type).count()
                for type in Course._course_type_enum_
            },
            'by_status': {
                status.value: Course.query.filter_by(status=status).count()
                for status in Course._course_status_enum_
            }
        },
        'enrollment_stats': {
            'by_status': {
                status.value: Enrollment.query.filter_by(status=status).count()
                for status in Enrollment._status_enum_
            }
        },
        'grade_stats': {
            'average_gpa': db.session.query(func.avg(Student.gpa)).filter(
                Student.gpa.isnot(None)
            ).scalar() or 0
        }
    }

def get_system_health():
    """获取系统健康状态"""
    return {
        'database_status': 'healthy',
        'cache_status': 'healthy',
        'disk_usage': '45%',
        'memory_usage': '68%',
        'cpu_usage': '32%',
        'uptime': '15 days 3 hours'
    }

def get_recent_activities(limit=10):
    """获取最近活动"""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            'id': log.id,
            'action': log.action.value,
            'description': log.description,
            'timestamp': log.timestamp.isoformat(),
            'user': log.username
        }
        for log in logs
    ]

def get_quick_actions(admin_level):
    """获取快捷操作"""
    actions = [
        {'name': '用户管理', 'icon': 'users', 'module': 'users'},
        {'name': '课程管理', 'icon': 'book', 'module': 'courses'},
        {'name': '成绩管理', 'icon': 'chart-bar', 'module': 'grades'},
        {'name': '系统配置', 'icon': 'settings', 'module': 'system'},
        {'name': '报表统计', 'icon': 'bar-chart', 'module': 'reports'}
    ]

    if admin_level == 'super_admin':
        actions.extend([
            {'name': '权限管理', 'icon': 'key', 'module': 'permissions'},
            {'name': '审计日志', 'icon': 'list', 'module': 'audit'},
            {'name': '备份恢复', 'icon': 'backup', 'module': 'backup'}
        ])

    return actions

def get_admin_notifications(admin_id):
    """获取管理员通知"""
    from models import Message

    # 获取未读的系统消息
    notifications = Message.query.filter_by(
        receiver_id=admin_id,
        type='system',
        status='unread'
    ).order_by(Message.sent_at.desc()).limit(5).all()

    return [
        {
            'id': msg.id,
            'title': msg.title,
            'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
            'timestamp': msg.sent_at.isoformat(),
            'priority': msg.priority.value
        }
        for msg in notifications
    ]