# ========================================
# 学生信息管理系统 - API模块初始化
# ========================================

from flask import Blueprint
from flask_restx import Api

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 创建API实例
api = Api(
    api_bp,
    version='1.0',
    title='学生信息管理系统 API',
    description='基于Flask和RESTful架构的学生信息管理系统后端API',
    doc='/docs/',
    prefix='/api/v1'
)

# 导入所有命名空间
from api.auth import auth_ns
from api.users import users_ns
from api.students import students_ns
from api.teachers import teachers_ns
from api.admins import admins_ns
from api.courses import courses_ns
from api.enrollments import enrollments_ns
from api.grades import grades_ns
from api.messages import messages_ns
from api.notifications import notifications_ns
from api.reports import reports_ns
from api.system import system_ns

# 注册所有命名空间
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(users_ns, path='/users')
api.add_namespace(students_ns, path='/students')
api.add_namespace(teachers_ns, path='/teachers')
api.add_namespace(admins_ns, path='/admins')
api.add_namespace(courses_ns, path='/courses')
api.add_namespace(enrollments_ns, path='/enrollments')
api.add_namespace(grades_ns, path='/grades')
api.add_namespace(messages_ns, path='/messages')
api.add_namespace(notifications_ns, path='/notifications')
api.add_namespace(reports_ns, path='/reports')
api.add_namespace(system_ns, path='/system')

# 导出蓝图
__all__ = ['api_bp']