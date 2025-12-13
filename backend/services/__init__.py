# ========================================
# 学生信息管理系统 - 业务逻辑层
# ========================================

"""
业务逻辑层 (Services Layer)

本层负责处理应用程序的核心业务逻辑，将业务规则与API控制器分离，
提供可重用的业务服务。

主要职责：
- 业务规则实现
- 数据验证和处理
- 服务组合和编排
- 事务管理
- 异常处理

架构特点：
- 依赖注入
- 单一职责原则
- 可测试性
- 可复用性
"""

from .base_service import BaseService
from .user_service import UserService
from .student_service import StudentService
from .teacher_service import TeacherService
from .course_service import CourseService
from .enrollment_service import EnrollmentService
from .grade_service import GradeService
from .message_service import MessageService
from .report_service import ReportService
from .system_service import SystemService

# 导出所有服务类
__all__ = [
    'BaseService',
    'UserService',
    'StudentService',
    'TeacherService',
    'CourseService',
    'EnrollmentService',
    'GradeService',
    'MessageService',
    'ReportService',
    'SystemService'
]

# 服务工厂
class ServiceFactory:
    """服务工厂类，用于创建和获取服务实例"""

    _instances = {}

    @classmethod
    def get_user_service(cls) -> UserService:
        """获取用户服务实例"""
        if 'user' not in cls._instances:
            cls._instances['user'] = UserService()
        return cls._instances['user']

    @classmethod
    def get_student_service(cls) -> StudentService:
        """获取学生服务实例"""
        if 'student' not in cls._instances:
            cls._instances['student'] = StudentService()
        return cls._instances['student']

    @classmethod
    def get_teacher_service(cls) -> TeacherService:
        """获取教师服务实例"""
        if 'teacher' not in cls._instances:
            cls._instances['teacher'] = TeacherService()
        return cls._instances['teacher']

    @classmethod
    def get_course_service(cls) -> CourseService:
        """获取课程服务实例"""
        if 'course' not in cls._instances:
            cls._instances['course'] = CourseService()
        return cls._instances['course']

    @classmethod
    def get_enrollment_service(cls) -> EnrollmentService:
        """获取选课服务实例"""
        if 'enrollment' not in cls._instances:
            cls._instances['enrollment'] = EnrollmentService()
        return cls._instances['enrollment']

    @classmethod
    def get_grade_service(cls) -> GradeService:
        """获取成绩服务实例"""
        if 'grade' not in cls._instances:
            cls._instances['grade'] = GradeService()
        return cls._instances['grade']

    @classmethod
    def get_message_service(cls) -> MessageService:
        """获取消息服务实例"""
        if 'message' not in cls._instances:
            cls._instances['message'] = MessageService()
        return cls._instances['message']

    @classmethod
    def get_report_service(cls) -> ReportService:
        """获取报表服务实例"""
        if 'report' not in cls._instances:
            cls._instances['report'] = ReportService()
        return cls._instances['report']

    @classmethod
    def get_system_service(cls) -> SystemService:
        """获取系统服务实例"""
        if 'system' not in cls._instances:
            cls._instances['system'] = SystemService()
        return cls._instances['system']

    @classmethod
    def clear_instances(cls):
        """清除所有服务实例（主要用于测试）"""
        cls._instances.clear()


# 便捷函数
def get_service(service_name: str):
    """
    获取指定服务实例

    Args:
        service_name: 服务名称

    Returns:
        对应的服务实例
    """
    service_map = {
        'user': ServiceFactory.get_user_service,
        'student': ServiceFactory.get_student_service,
        'teacher': ServiceFactory.get_teacher_service,
        'course': ServiceFactory.get_course_service,
        'enrollment': ServiceFactory.get_enrollment_service,
        'grade': ServiceFactory.get_grade_service,
        'message': ServiceFactory.get_message_service,
        'report': ServiceFactory.get_report_service,
        'system': ServiceFactory.get_system_service
    }

    if service_name not in service_map:
        raise ValueError(f"未知的服务名称: {service_name}")

    return service_map[service_name]()