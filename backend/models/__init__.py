# ========================================
# 学生信息管理系统 - 数据模型初始化
# ========================================

from models.user import User, UserProfile
from models.student import Student
from models.teacher import Teacher
from models.admin import Admin
from models.course import Course
from models.enrollment import Enrollment
from models.grade import Grade
from models.message import Message, MessageTemplate
from models.audit_log import AuditLog
from models.system_config import SystemConfig

# 导出所有模型类
__all__ = [
    'User',
    'UserProfile',
    'Student',
    'Teacher',
    'Admin',
    'Course',
    'Enrollment',
    'Grade',
    'Message',
    'MessageTemplate',
    'AuditLog',
    'SystemConfig',
]