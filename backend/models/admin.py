# ========================================
# 学生信息管理系统 - 管理员模型
# ========================================

import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class AdminLevel(enum.Enum):
    """管理员级别枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    SYSTEM_ADMIN = "system_admin"  # 系统管理员
    DEPARTMENT_ADMIN = "department_admin"  # 部门管理员
    GENERAL_ADMIN = "general_admin"  # 普通管理员

class Admin(BaseModel):
    """管理员模型"""

    __tablename__ = 'admins'

    user_id = Column(db.CHAR(36), db.ForeignKey('users.id'), unique=True, nullable=False)

    # 管理员信息
    admin_id = Column(String(20), unique=True, nullable=False, index=True)
    level = Column(Enum(AdminLevel), nullable=False)
    department = Column(String(100))  # 所属部门

    # 权限配置
    permissions = Column(JSON)  # 详细权限列表
    is_super_admin = Column(Boolean, default=False)

    # 管理范围
    managed_departments = Column(JSON)  # 管理的部门列表
    managed_functions = Column(JSON)  # 管理的功能模块

    # 其他信息
    notes = Column(db.Text)
    last_password_change = Column(db.DateTime)
    two_factor_enabled = Column(Boolean, default=False)

    # 关系
    user = relationship("User", backref="admin_record")

    # 索引
    __table_args__ = (
        Index('idx_admin_id_level', 'admin_id', 'level'),
        Index('idx_department_level', 'department', 'level'),
    )

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)

        # 如果是超级管理员，设置默认权限
        if self.is_super_admin or self.level == AdminLevel.SUPER_ADMIN:
            self.permissions = self._get_default_super_admin_permissions()
        elif not self.permissions:
            self.permissions = self._get_default_permissions_by_level()

    @property
    def full_admin_id(self):
        """获取完整管理员编号"""
        return f"ADMIN{self.admin_id.zfill(3)}"

    @property
    def display_level(self):
        """获取显示级别"""
        level_mapping = {
            AdminLevel.SUPER_ADMIN: "超级管理员",
            AdminLevel.SYSTEM_ADMIN: "系统管理员",
            AdminLevel.DEPARTMENT_ADMIN: "部门管理员",
            AdminLevel.GENERAL_ADMIN: "普通管理员"
        }
        return level_mapping.get(self.level, "管理员")

    def _get_default_super_admin_permissions(self):
        """获取超级管理员默认权限"""
        return {
            'user_management': True,
            'student_management': True,
            'teacher_management': True,
            'course_management': True,
            'grade_management': True,
            'system_config': True,
            'data_import_export': True,
            'reports': True,
            'audit_logs': True,
            'message_management': True,
            'backup_restore': True,
            'permission_management': True
        }

    def _get_default_permissions_by_level(self):
        """根据级别获取默认权限"""
        if self.level == AdminLevel.SYSTEM_ADMIN:
            return {
                'user_management': True,
                'system_config': True,
                'data_import_export': True,
                'reports': True,
                'audit_logs': True,
                'message_management': True,
                'backup_restore': True
            }
        elif self.level == AdminLevel.DEPARTMENT_ADMIN:
            return {
                'student_management': True,
                'teacher_management': True,
                'course_management': True,
                'grade_management': True,
                'reports': True,
                'message_management': True
            }
        elif self.level == AdminLevel.GENERAL_ADMIN:
            return {
                'student_management': True,
                'course_management': True,
                'grade_management': True,
                'reports': True
            }
        else:
            return {}

    def has_permission(self, permission):
        """检查是否有指定权限"""
        if not self.permissions:
            return False

        # 超级管理员拥有所有权限
        if self.is_super_admin or self.level == AdminLevel.SUPER_ADMIN:
            return True

        # 检查具体权限
        return self.permissions.get(permission, False)

    def add_permission(self, permission):
        """添加权限"""
        if not self.permissions:
            self.permissions = {}
        self.permissions[permission] = True
        self.save()

    def remove_permission(self, permission):
        """移除权限"""
        if self.permissions and permission in self.permissions:
            self.permissions[permission] = False
            self.save()

    def set_permissions(self, permissions_dict):
        """设置权限字典"""
        self.permissions = permissions_dict
        self.save()

    def can_manage_department(self, department):
        """检查是否可以管理指定部门"""
        # 超级管理员可以管理所有部门
        if self.is_super_admin or self.level == AdminLevel.SUPER_ADMIN:
            return True

        # 系统管理员可以管理所有部门
        if self.level == AdminLevel.SYSTEM_ADMIN:
            return True

        # 检查管理范围
        if self.managed_departments:
            return department in self.managed_departments

        # 部门管理员只能管理自己的部门
        if self.level == AdminLevel.DEPARTMENT_ADMIN:
            return department == self.department

        return False

    def can_access_function(self, function):
        """检查是否可以访问指定功能"""
        if self.managed_functions:
            return function in self.managed_functions
        return True

    def get_accessible_departments(self):
        """获取可管理的部门列表"""
        if self.is_super_admin or self.level == AdminLevel.SUPER_ADMIN:
            return None  # 表示所有部门

        if self.level == AdminLevel.SYSTEM_ADMIN:
            return None  # 表示所有部门

        return self.managed_departments or [self.department]

    def get_accessible_functions(self):
        """获取可访问的功能列表"""
        if self.managed_functions:
            return self.managed_functions
        return ['all']

    def update_last_password_change(self):
        """更新最后密码修改时间"""
        from datetime import datetime
        self.last_password_change = datetime.utcnow()
        self.save()

    def enable_two_factor(self):
        """启用双因素认证"""
        self.two_factor_enabled = True
        self.save()

    def disable_two_factor(self):
        """禁用双因素认证"""
        self.two_factor_enabled = False
        self.save()

    def get_permission_summary(self):
        """获取权限摘要"""
        if not self.permissions:
            return "无特殊权限"

        active_permissions = [k for k, v in self.permissions.items() if v]

        permission_categories = {
            'user_management': '用户管理',
            'student_management': '学生管理',
            'teacher_management': '教师管理',
            'course_management': '课程管理',
            'grade_management': '成绩管理',
            'system_config': '系统配置',
            'data_import_export': '数据导入导出',
            'reports': '报表统计',
            'audit_logs': '审计日志',
            'message_management': '消息管理',
            'backup_restore': '备份恢复',
            'permission_management': '权限管理'
        }

        active_names = [permission_categories.get(p, p) for p in active_permissions]
        return ', '.join(active_names)

    def promote_to_super_admin(self):
        """提升为超级管理员"""
        self.level = AdminLevel.SUPER_ADMIN
        self.is_super_admin = True
        self.permissions = self._get_default_super_admin_permissions()
        self.save()

    def demote_from_super_admin(self, new_level):
        """从超级管理员降级"""
        self.level = new_level
        self.is_super_admin = False
        self.permissions = self._get_default_permissions_by_level()
        self.save()

    def get_audit_logs_for_user(self, user_id, limit=100):
        """获取指定用户的审计日志"""
        from .audit_log import AuditLog
        return AuditLog.query.filter_by(
            user_id=user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()

    def get_system_statistics(self):
        """获取系统统计信息"""
        from .user import User, UserRole
        from .student import Student
        from .teacher import Teacher
        from .course import Course
        from .enrollment import Enrollment

        stats = {}

        if self.has_permission('user_management'):
            stats['total_users'] = User.query.count()
            stats['admin_users'] = User.query.filter_by(role=UserRole.ADMIN).count()
            stats['teacher_users'] = User.query.filter_by(role=UserRole.TEACHER).count()
            stats['student_users'] = User.query.filter_by(role=UserRole.STUDENT).count()

        if self.has_permission('student_management'):
            stats['total_students'] = Student.query.count()
            stats['active_students'] = Student.query.filter_by(academic_status='enrolled').count()

        if self.has_permission('teacher_management'):
            stats['total_teachers'] = Teacher.query.count()
            stats['active_teachers'] = Teacher.query.filter_by(status='active').count()

        if self.has_permission('course_management'):
            stats['total_courses'] = Course.query.count()
            stats['active_courses'] = Course.query.filter_by(status='active').count()

        if self.has_permission('grade_management'):
            stats['total_enrollments'] = Enrollment.query.count()

        return stats

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        if not include_sensitive:
            # 移除敏感信息
            data.pop('permissions', None)
            data.pop('managed_departments', None)
            data.pop('managed_functions', None)
        return data

    def __repr__(self):
        return f"<Admin(admin_id='{self.admin_id}', level='{self.level.value}', name='{self.user.profile.full_name if self.user.profile else self.user.username}')>"