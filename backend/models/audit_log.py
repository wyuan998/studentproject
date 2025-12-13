# ========================================
# 学生信息管理系统 - 审计日志模型
# ========================================

import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class AuditAction(enum.Enum):
    """审计动作枚举"""
    CREATE = "create"           # 创建
    UPDATE = "update"           # 更新
    DELETE = "delete"           # 删除
    LOGIN = "login"             # 登录
    LOGOUT = "logout"           # 登出
    ACCESS = "access"           # 访问
    EXPORT = "export"           # 导出
    IMPORT = "import"           # 导入
    BACKUP = "backup"           # 备份
    RESTORE = "restore"         # 恢复
    PERMISSION_CHANGE = "permission_change"  # 权限变更
    PASSWORD_CHANGE = "password_change"      # 密码修改
    SYSTEM_CONFIG = "system_config"          # 系统配置修改

class AuditLog(BaseModel):
    """审计日志模型"""

    __tablename__ = 'audit_logs'

    # 用户信息
    user_id = Column(db.CHAR(36), db.ForeignKey('users.id'))
    username = Column(String(50))  # 冗余存储用户名
    user_role = Column(String(20))  # 冗余存储用户角色

    # 动作信息
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(50))  # 资源类型
    resource_id = Column(db.CHAR(36))    # 资源ID
    resource_name = Column(String(100))  # 资源名称

    # 请求信息
    ip_address = Column(String(45))  # IP地址
    user_agent = Column(Text)        # 用户代理
    endpoint = Column(String(200))   # 接口端点
    http_method = Column(String(10)) # HTTP方法

    # 操作详情
    description = Column(Text)  # 操作描述
    details = Column(JSON)      # 详细信息（JSON格式）
    old_values = Column(JSON)   # 旧值
    new_values = Column(JSON)   # 新值

    # 结果信息
    success = Column(db.Boolean, default=True)  # 是否成功
    error_message = Column(Text)               # 错误信息
    status_code = Column(db.Integer)           # HTTP状态码

    # 时间信息
    timestamp = Column(db.DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(db.Integer)  # 操作耗时（毫秒）

    # 其他信息
    session_id = Column(String(100))   # 会话ID
    request_id = Column(String(100))   # 请求ID
    batch_id = Column(String(100))     # 批次ID（用于批量操作）

    # 关系
    user = relationship("User", backref="audit_logs")

    # 索引
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
        Index('idx_ip_timestamp', 'ip_address', 'timestamp'),
        Index('idx_batch_id', 'batch_id'),
    )

    def __init__(self, **kwargs):
        super(AuditLog, self).__init__(**kwargs)
        if not self.timestamp:
            self.timestamp = datetime.utcnow()

    @property
    def display_action(self):
        """获取动作显示名称"""
        action_mapping = {
            AuditAction.CREATE: "创建",
            AuditAction.UPDATE: "更新",
            AuditAction.DELETE: "删除",
            AuditAction.LOGIN: "登录",
            AuditAction.LOGOUT: "登出",
            AuditAction.ACCESS: "访问",
            AuditAction.EXPORT: "导出",
            AuditAction.IMPORT: "导入",
            AuditAction.BACKUP: "备份",
            AuditAction.RESTORE: "恢复",
            AuditAction.PERMISSION_CHANGE: "权限变更",
            AuditAction.PASSWORD_CHANGE: "密码修改",
            AuditAction.SYSTEM_CONFIG: "系统配置修改"
        }
        return action_mapping.get(self.action, "操作")

    @property
    def resource_identifier(self):
        """获取资源标识"""
        if self.resource_name:
            return f"{self.resource_type}: {self.resource_name}"
        elif self.resource_id:
            return f"{self.resource_type}: {self.resource_id}"
        elif self.resource_type:
            return self.resource_type
        return "未知资源"

    @property
    def is_sensitive_operation(self):
        """是否为敏感操作"""
        sensitive_actions = [
            AuditAction.DELETE,
            AuditAction.PERMISSION_CHANGE,
            AuditAction.PASSWORD_CHANGE,
            AuditAction.SYSTEM_CONFIG,
            AuditAction.IMPORT,
            AuditAction.RESTORE
        ]
        return self.action in sensitive_actions

    @property
    def is_failed_operation(self):
        """是否为失败操作"""
        return not self.success

    @classmethod
    def log_action(cls, action, user_id=None, resource_type=None, resource_id=None,
                   description=None, details=None, success=True, **kwargs):
        """记录审计日志"""
        from flask import request, g

        # 获取当前用户信息
        current_user_id = user_id
        current_username = None
        current_user_role = None

        if not current_user_id and hasattr(g, 'current_user'):
            current_user_id = g.current_user.id if g.current_user else None
            current_username = g.current_user.username if g.current_user else None
            current_user_role = g.current_user.role.value if g.current_user and g.current_user.role else None

        # 获取请求信息
        ip_address = kwargs.get('ip_address') or (request.remote_addr if request else None)
        user_agent = kwargs.get('user_agent') or (request.headers.get('User-Agent') if request else None)
        endpoint = kwargs.get('endpoint') or (request.endpoint if request else None)
        http_method = kwargs.get('http_method') or (request.method if request else None)

        # 获取资源名称
        resource_name = kwargs.get('resource_name')
        if not resource_name and resource_id and resource_type:
            resource_name = cls._get_resource_name(resource_type, resource_id)

        audit_log = cls(
            user_id=current_user_id,
            username=current_username,
            user_role=current_user_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            description=description,
            details=details,
            old_values=kwargs.get('old_values'),
            new_values=kwargs.get('new_values'),
            success=success,
            error_message=kwargs.get('error_message'),
            status_code=kwargs.get('status_code'),
            duration_ms=kwargs.get('duration_ms'),
            session_id=kwargs.get('session_id'),
            request_id=kwargs.get('request_id'),
            batch_id=kwargs.get('batch_id')
        )

        audit_log.save()
        return audit_log

    @classmethod
    def log_create(cls, user_id, resource_type, resource_id, resource_name=None, details=None):
        """记录创建操作"""
        return cls.log_action(
            action=AuditAction.CREATE,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            description=f"创建{resource_type}: {resource_name or resource_id}"
        )

    @classmethod
    def log_update(cls, user_id, resource_type, resource_id, resource_name=None,
                   old_values=None, new_values=None, details=None):
        """记录更新操作"""
        description = f"更新{resource_type}: {resource_name or resource_id}"
        if old_values and new_values:
            changed_fields = []
            for key in new_values:
                if key in old_values and old_values[key] != new_values[key]:
                    changed_fields.append(key)
            if changed_fields:
                description += f" (修改字段: {', '.join(changed_fields)})"

        return cls.log_action(
            action=AuditAction.UPDATE,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            details=details,
            description=description
        )

    @classmethod
    def log_delete(cls, user_id, resource_type, resource_id, resource_name=None, details=None):
        """记录删除操作"""
        return cls.log_action(
            action=AuditAction.DELETE,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            description=f"删除{resource_type}: {resource_name or resource_id}"
        )

    @classmethod
    def log_login(cls, user_id, username, success=True, error_message=None):
        """记录登录操作"""
        return cls.log_action(
            action=AuditAction.LOGIN,
            user_id=user_id,
            username=username,
            success=success,
            error_message=error_message,
            description=f"用户{username}{'登录成功' if success else '登录失败'}"
        )

    @classmethod
    def log_export(cls, user_id, resource_type, details=None, **kwargs):
        """记录导出操作"""
        return cls.log_action(
            action=AuditAction.EXPORT,
            user_id=user_id,
            resource_type=resource_type,
            details=details,
            description=f"导出{resource_type}数据",
            **kwargs
        )

    @classmethod
    def log_import(cls, user_id, resource_type, details=None, **kwargs):
        """记录导入操作"""
        return cls.log_action(
            action=AuditAction.IMPORT,
            user_id=user_id,
            resource_type=resource_type,
            details=details,
            description=f"导入{resource_type}数据",
            **kwargs
        )

    @classmethod
    def _get_resource_name(cls, resource_type, resource_id):
        """根据资源类型和ID获取资源名称"""
        try:
            if resource_type == 'user':
                from .user import User
                user = User.query.get(resource_id)
                if user and user.profile:
                    return user.profile.full_name
                elif user:
                    return user.username
            elif resource_type == 'student':
                from .student import Student
                student = Student.query.get(resource_id)
                if student and student.user and student.user.profile:
                    return student.user.profile.full_name
                elif student:
                    return student.student_id
            elif resource_type == 'teacher':
                from .teacher import Teacher
                teacher = Teacher.query.get(resource_id)
                if teacher and teacher.user and teacher.user.profile:
                    return teacher.user.profile.full_name
                elif teacher:
                    return teacher.teacher_id
            elif resource_type == 'course':
                from .course import Course
                course = Course.query.get(resource_id)
                if course:
                    return f"{course.course_code} - {course.name}"
            elif resource_type == 'grade':
                from .grade import Grade
                grade = Grade.query.get(resource_id)
                if grade and grade.student and grade.course:
                    return f"{grade.student.student_id} - {grade.course.course_code}"
        except Exception:
            pass

        return None

    @classmethod
    def get_user_logs(cls, user_id, limit=100, action=None, start_date=None, end_date=None):
        """获取用户审计日志"""
        query = cls.query.filter_by(user_id=user_id)

        if action:
            query = query.filter_by(action=action)

        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)

        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_resource_logs(cls, resource_type, resource_id=None, limit=100):
        """获取资源审计日志"""
        query = cls.query.filter_by(resource_type=resource_type)

        if resource_id:
            query = query.filter_by(resource_id=resource_id)

        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_failed_logs(cls, limit=100, start_date=None):
        """获取失败操作日志"""
        query = cls.query.filter_by(success=False)

        if start_date:
            query = query.filter(cls.timestamp >= start_date)

        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_sensitive_logs(cls, limit=100, start_date=None):
        """获取敏感操作日志"""
        sensitive_actions = [
            AuditAction.DELETE,
            AuditAction.PERMISSION_CHANGE,
            AuditAction.PASSWORD_CHANGE,
            AuditAction.SYSTEM_CONFIG,
            AuditAction.IMPORT,
            AuditAction.RESTORE
        ]

        query = cls.query.filter(cls.action.in_(sensitive_actions))

        if start_date:
            query = query.filter(cls.timestamp >= start_date)

        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_login_logs(cls, user_id=None, limit=100, start_date=None, success_only=None):
        """获取登录日志"""
        query = cls.query.filter_by(action=AuditAction.LOGIN)

        if user_id:
            query = query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(cls.timestamp >= start_date)

        if success_only is not None:
            query = query.filter_by(success=success_only)

        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_statistics(cls, start_date=None, end_date=None):
        """获取审计统计信息"""
        query = cls.query

        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)

        total_logs = query.count()
        success_logs = query.filter_by(success=True).count()
        failed_logs = query.filter_by(success=False).count()

        # 按动作统计
        action_stats = db.session.query(
            cls.action, db.func.count(cls.id).label('count')
        ).filter(
            cls.timestamp >= start_date if start_date else True,
            cls.timestamp <= end_date if end_date else True
        ).group_by(cls.action).all()

        # 按用户统计（前10名最活跃用户）
        user_stats = db.session.query(
            cls.username, db.func.count(cls.id).label('count')
        ).filter(
            cls.timestamp >= start_date if start_date else True,
            cls.timestamp <= end_date if end_date else True,
            cls.user_id.isnot(None)
        ).group_by(cls.username).order_by(
            db.func.count(cls.id).desc()
        ).limit(10).all()

        return {
            'total_logs': total_logs,
            'success_logs': success_logs,
            'failed_logs': failed_logs,
            'success_rate': (success_logs / total_logs * 100) if total_logs > 0 else 0,
            'action_stats': dict([(action.value, count) for action, count in action_stats]),
            'user_stats': dict([(username, count) for username, count in user_stats])
        }

    @classmethod
    def cleanup_old_logs(cls, days=365):
        """清理旧日志"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = cls.query.filter(cls.timestamp < cutoff_date).count()
        cls.query.filter(cls.timestamp < cutoff_date).delete()
        db.session.commit()

        return deleted_count

    def to_dict(self, include_user=True):
        """转换为字典"""
        data = super().to_dict()
        data['display_action'] = self.display_action
        data['resource_identifier'] = self.resource_identifier
        data['is_sensitive_operation'] = self.is_sensitive_operation
        data['is_failed_operation'] = self.is_failed_operation

        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'name': self.user.profile.full_name if self.user.profile else self.user.username,
                'role': self.user.role.value
            }

        return data

    def __repr__(self):
        return f"<AuditLog(action='{self.action.value}', user='{self.username}', resource='{self.resource_identifier}', timestamp='{self.timestamp}')>"