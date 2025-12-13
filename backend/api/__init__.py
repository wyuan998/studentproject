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
from .auth import auth as auth_ns
from .users import users as users_ns
from .students import students as students_ns
from .teachers import teachers as teachers_ns
from .admin import admin as admin_ns
from .courses import courses as courses_ns
from .enrollments import enrollments as enrollments_ns
from .grades import grades as grades_ns
from .messages import messages as messages_ns
from .system_config import api as system_config_ns
from .reports import reports as reports_ns

# 注册所有命名空间
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(users_ns, path='/users')
api.add_namespace(students_ns, path='/students')
api.add_namespace(teachers_ns, path='/teachers')
api.add_namespace(admin_ns, path='/admin')
api.add_namespace(courses_ns, path='/courses')
api.add_namespace(enrollments_ns, path='/enrollments')
api.add_namespace(grades_ns, path='/grades')
api.add_namespace(messages_ns, path='/messages')
api.add_namespace(system_config_ns, path='/system-config')
api.add_namespace(reports_ns, path='/reports')

# 导出蓝图
__all__ = ['api_bp']