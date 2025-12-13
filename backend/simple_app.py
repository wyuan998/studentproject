# ========================================
# 学生信息管理系统 - 简化启动文件
# ========================================

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# 创建Flask应用
app = Flask(__name__)

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟数据存储
users = []
students = []
teachers = []
courses = []

# 初始化一些示例数据
def init_sample_data():
    """初始化示例数据"""
    if not users:
        # 添加管理员用户
        users.append({
            'id': 1,
            'username': 'admin',
            'password': '123456',  # 实际应用中应该加密
            'real_name': '系统管理员',
            'email': 'admin@example.com',
            'role': 'admin',
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        })

        # 添加示例学生
        students.append({
            'id': 1,
            'student_id': 'S2021001',
            'name': '张三',
            'gender': '男',
            'birth_date': '2000-01-01',
            'phone': '13800138001',
            'email': 'zhangsan@example.com',
            'major': '计算机科学',
            'class_name': '计算机科学1班',
            'enrollment_date': '2021-09-01',
            'status': 'active'
        })

        # 添加示例教师
        teachers.append({
            'id': 1,
            'teacher_id': 'T001',
            'name': '李老师',
            'gender': '女',
            'birth_date': '1980-01-01',
            'phone': '13800138002',
            'email': 'teacher@example.com',
            'department': '计算机科学系',
            'title': '教授',
            'hire_date': '2010-09-01',
            'status': 'active'
        })

        # 添加示例课程
        courses.append({
            'id': 1,
            'course_code': 'CS101',
            'course_name': '计算机科学导论',
            'credits': 3,
            'hours': 48,
            'teacher_id': 1,
            'teacher_name': '李老师',
            'semester': '2024-春季',
            'max_students': 50,
            'current_students': 25,
            'description': '计算机科学基础课程'
        })

# 路由定义
@app.route('/')
def index():
    """首页路由"""
    return jsonify({
        'message': '学生信息管理系统 API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# 认证相关路由
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # 简单的用户验证（实际应用中应该更安全）
    user = None
    for u in users:
        if u['username'] == username and u['password'] == password:
            user = u
            break

    if user:
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'real_name': user['real_name'],
                    'email': user['email'],
                    'role': user['role']
                },
                'token': 'mock-jwt-token-' + str(user['id'])
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

# 学生管理路由
@app.route('/api/students', methods=['GET'])
def get_students():
    """获取学生列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')

    # 简单的过滤逻辑
    filtered_students = students
    if keyword:
        filtered_students = [s for s in students
                          if keyword.lower() in s['name'].lower()
                          or keyword.lower() in s['student_id'].lower()]

    return jsonify({
        'success': True,
        'data': {
            'students': filtered_students,
            'total': len(filtered_students),
            'page': page,
            'pageSize': page_size
        }
    })

@app.route('/api/students', methods=['POST'])
def create_student():
    """创建学生"""
    data = request.get_json()
    new_student = {
        'id': len(students) + 1,
        **data,
        'created_at': datetime.now().isoformat()
    }
    students.append(new_student)

    return jsonify({
        'success': True,
        'message': '学生创建成功',
        'data': new_student
    })

# 教师管理路由
@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """获取教师列表"""
    return jsonify({
        'success': True,
        'data': {
            'teachers': teachers,
            'total': len(teachers)
        }
    })

# 课程管理路由
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """获取课程列表"""
    return jsonify({
        'success': True,
        'data': {
            'courses': courses,
            'total': len(courses)
        }
    })

# 用户信息路由
@app.route('/api/auth/user', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    # 模拟从token中获取用户信息
    return jsonify({
        'success': True,
        'data': {
            'id': 1,
            'username': 'admin',
            'real_name': '系统管理员',
            'email': 'admin@example.com',
            'role': 'admin',
            'avatar': '',
            'permissions': ['read', 'write', 'delete'],
            'created_at': datetime.now().isoformat()
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({
        'success': True,
        'message': '退出成功'
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'API接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("学生信息管理系统 - 后端服务启动")
    print("=" * 50)
    print(f"服务地址: http://localhost:5000")
    print(f"API文档: http://localhost:5000/api/health")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print("默认管理员账号:")
    print("   用户名: admin")
    print("   密码: 123456")
    print("=" * 50)
    print("系统正在启动中...")

    # 初始化示例数据
    init_sample_data()

    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )