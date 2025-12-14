# ========================================
# 学生信息管理系统 - 数据序列化模式初始化
# ========================================

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from extensions import ma
from models import (
    User, UserProfile, Student, Teacher, Admin, Course,
    Enrollment, Grade, Message, MessageTemplate,
    AuditLog, SystemConfig
)

# 导入所有序列化模式
from schemas.user import UserSchema, UserProfileSchema, UserCreateSchema, UserUpdateSchema, UserRegisterSchema
from schemas.student import StudentSchema, StudentCreateSchema, StudentUpdateSchema
from schemas.teacher import TeacherSchema, TeacherCreateSchema, TeacherUpdateSchema
from schemas.admin import AdminSchema, AdminCreateSchema, AdminUpdateSchema
from schemas.course import CourseSchema, CourseCreateSchema, CourseUpdateSchema
from schemas.enrollment import EnrollmentSchema, EnrollmentCreateSchema, EnrollmentUpdateSchema
from schemas.grade import GradeSchema, GradeCreateSchema, GradeUpdateSchema
from schemas.message import MessageSchema, MessageCreateSchema, MessageUpdateSchema
from schemas.message_template import MessageTemplateSchema, MessageTemplateCreateSchema, MessageTemplateUpdateSchema
from schemas.audit_log import AuditLogSchema
from schemas.system_config import SystemConfigSchema, SystemConfigCreateSchema, SystemConfigUpdateSchema

# 导出所有模式类
__all__ = [
    # Marshmallow实例
    'ma',

    # 基础模式类
    'Schema',
    'fields',
    'validate',
    'validates',
    'validates_schema',
    'ValidationError',

    # 用户相关
    'UserSchema',
    'UserProfileSchema',
    'UserCreateSchema',
    'UserUpdateSchema',
    'UserRegisterSchema',

    # 学生相关
    'StudentSchema',
    'StudentCreateSchema',
    'StudentUpdateSchema',

    # 教师相关
    'TeacherSchema',
    'TeacherCreateSchema',
    'TeacherUpdateSchema',

    # 管理员相关
    'AdminSchema',
    'AdminCreateSchema',
    'AdminUpdateSchema',

    # 课程相关
    'CourseSchema',
    'CourseCreateSchema',
    'CourseUpdateSchema',

    # 选课相关
    'EnrollmentSchema',
    'EnrollmentCreateSchema',
    'EnrollmentUpdateSchema',

    # 成绩相关
    'GradeSchema',
    'GradeCreateSchema',
    'GradeUpdateSchema',

    # 消息相关
    'MessageSchema',
    'MessageCreateSchema',
    'MessageUpdateSchema',

    # 消息模板相关
    'MessageTemplateSchema',
    'MessageTemplateCreateSchema',
    'MessageTemplateUpdateSchema',

    # 审计日志相关
    'AuditLogSchema',

    # 系统配置相关
    'SystemConfigSchema',
    'SystemConfigCreateSchema',
    'SystemConfigUpdateSchema',
]