# ========================================
# 学生信息管理系统 - 用户模型
# ========================================

import enum
from sqlalchemy import Column, String, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    """用户模型"""

    __tablename__ = 'users'

    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # 角色和状态
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)

    # 验证状态
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    # 登录信息
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)

    # 关系
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # 根据角色动态关系
    @property
    def student_profile(self):
        if self.role == UserRole.STUDENT:
            return relationship("Student", back_populates="user")
        return None

    @property
    def teacher_profile(self):
        if self.role == UserRole.TEACHER:
            return relationship("Teacher", back_populates="user")
        return None

    @property
    def admin_profile(self):
        if self.role == UserRole.ADMIN:
            return relationship("Admin", back_populates="user")
        return None

    # 索引
    __table_args__ = (
        Index('idx_username_email', 'username', 'email'),
        Index('idx_role_status', 'role', 'status'),
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email and not self.email_verified:
            self.email_verified = False

    def is_active(self):
        """检查用户是否激活"""
        return self.status == UserStatus.ACTIVE

    def is_locked(self):
        """检查用户是否被锁定"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def can_login(self):
        """检查用户是否可以登录"""
        return self.is_active() and not self.is_locked()

    def update_login_info(self, ip_address=None):
        """更新登录信息"""
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
        self.login_count = (self.login_count or 0) + 1
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save()

    def record_failed_login(self):
        """记录登录失败"""
        from flask import current_app

        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)

        if self.failed_login_attempts >= max_attempts:
            # 锁定账户30分钟
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)

        self.save()

    def has_role(self, role):
        """检查用户是否有指定角色"""
        return self.role == role

    def has_permission(self, permission):
        """检查用户是否有指定权限"""
        if self.role == UserRole.ADMIN:
            # 管理员通过admin_profile检查权限
            if hasattr(self, 'admin_profile') and self.admin_profile:
                return self.admin_profile.has_permission(permission)
            return False
        elif self.role == UserRole.TEACHER:
            # 教师权限
            teacher_permissions = {
                'view_students', 'manage_grades', 'view_courses', 'manage_attendance'
            }
            return permission in teacher_permissions
        elif self.role == UserRole.STUDENT:
            # 学生权限
            student_permissions = {
                'view_profile', 'view_grades', 'view_courses', 'manage_enrollment'
            }
            return permission in student_permissions

        return False

    def get_display_name(self):
        """获取显示名称"""
        if self.profile:
            return f"{self.profile.first_name} {self.profile.last_name}"
        return self.username

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role.value}')>"

class UserProfile(BaseModel):
    """用户资料模型"""

    __tablename__ = 'user_profiles'

    user_id = Column(db.CHAR(36), db.ForeignKey('users.id'), unique=True, nullable=False)

    # 基本信息
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))

    # 个人信息
    gender = Column(db.Enum('male', 'female', 'other', name='gender_enum'))
    birthday = db.Column(db.Date)
    avatar = db.Column(db.String(255))

    # 地址信息
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='中国')

    # 教育信息
    department = db.Column(db.String(100))
    major = db.Column(db.String(100))
    degree = db.Column(db.String(50))

    # 紧急联系人
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))

    # 其他信息
    bio = db.Column(db.Text)
    social_links = db.Column(db.JSON)
    preferences = db.Column(db.JSON)

    # 关系
    user = relationship("User", back_populates="profile")

    def __init__(self, **kwargs):
        super(UserProfile, self).__init__(**kwargs)
        if not self.preferences:
            self.preferences = {}

    @property
    def full_name(self):
        """获取全名"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_phone(self):
        """获取显示电话（隐藏部分数字）"""
        if self.phone and len(self.phone) >= 7:
            return f"{self.phone[:3]}****{self.phone[-4:]}"
        return self.phone

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        if not include_sensitive:
            # 移除敏感信息
            data.pop('phone', None)
            data.pop('address', None)
            data.pop('emergency_contact_phone', None)
        return data

    def __repr__(self):
        return f"<UserProfile(user_id='{self.user_id}', name='{self.full_name}')>"