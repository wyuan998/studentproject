# ========================================
# 学生信息管理系统 - 简化登录服务
# ========================================

from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 存储token的简单内存存储
tokens = {}

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'success',
        'message': 'API服务运行正常',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')

    # 演示登录逻辑
    if username == 'admin' and password == '123456':
        token = f'demo-jwt-token-admin-{int(datetime.now().timestamp())}'
        refresh_token = f'demo-refresh-token-admin-{int(datetime.now().timestamp())}'

        user_data = {
            'id': 1,
            'username': 'admin',
            'real_name': '系统管理员',
            'email': 'admin@example.com',
            'role': 'admin',
            'roles': ['admin'],
            'avatar': None,
            'permissions': [
                'user:read', 'user:write', 'user:delete',
                'student:read', 'student:write', 'student:delete',
                'teacher:read', 'teacher:write', 'teacher:delete',
                'course:read', 'course:write', 'course:delete',
                'grade:read', 'grade:write', 'grade:delete',
                'system:read', 'system:write'
            ]
        }

        # 保存token到内存
        tokens[token] = user_data

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': token,
                'refresh_token': refresh_token,
                'user_info': user_data
            }
        })

    elif username == 'student' and password == '123456':
        token = f'demo-jwt-token-student-{int(datetime.now().timestamp())}'
        refresh_token = f'demo-refresh-token-student-{int(datetime.now().timestamp())}'

        user_data = {
            'id': 2,
            'username': 'student',
            'real_name': '张同学',
            'email': 'student@example.com',
            'role': 'student',
            'roles': ['student'],
            'avatar': None,
            'permissions': [
                'course:read',
                'grade:read'
            ]
        }

        tokens[token] = user_data

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': token,
                'refresh_token': refresh_token,
                'user_info': user_data
            }
        })

    elif username == 'teacher' and password == '123456':
        token = f'demo-jwt-token-teacher-{int(datetime.now().timestamp())}'
        refresh_token = f'demo-refresh-token-teacher-{int(datetime.now().timestamp())}'

        user_data = {
            'id': 3,
            'username': 'teacher',
            'real_name': '李老师',
            'email': 'teacher@example.com',
            'role': 'teacher',
            'roles': ['teacher'],
            'avatar': None,
            'permissions': [
                'student:read', 'student:write',
                'course:read', 'course:write',
                'grade:read', 'grade:write'
            ]
        }

        tokens[token] = user_data

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': token,
                'refresh_token': refresh_token,
                'user_info': user_data
            }
        })

    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({
        'success': True,
        'message': '登出成功'
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息（简化版）"""
    # 演示：返回默认用户信息
    return jsonify({
        'success': True,
        'data': {
            'id': 1,
            'username': 'admin',
            'real_name': '系统管理员',
            'email': 'admin@example.com',
            'role': 'admin',
            'roles': ['admin'],
            'avatar': None,
            'last_login': datetime.now().isoformat()
        }
    })

@app.route('/api/auth/user', methods=['GET'])
def get_current_user_alt():
    """获取当前用户信息（兼容）"""
    return get_current_user()

# 简单的CRUD端点
@app.route('/api/students', methods=['GET', 'POST'])
def students():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'students': [],
                'total': 0,
                'page': 1,
                'pageSize': 20
            },
            'message': '获取学生列表成功'
        })
    else:  # POST
        return jsonify({
            'success': True,
            'message': '创建学生成功',
            'data': {
                'id': 1,
                'name': '新学生',
                'created_at': datetime.now().isoformat()
            }
        })

@app.route('/api/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'courses': [],
                'total': 0,
                'page': 1,
                'pageSize': 20
            },
            'message': '获取课程列表成功'
        })
    else:  # POST
        return jsonify({
            'success': True,
            'message': '创建课程成功',
            'data': {
                'id': 1,
                'name': '新课程',
                'created_at': datetime.now().isoformat()
            }
        })

@app.route('/api/grades', methods=['GET'])
def grades():
    # 返回示例成绩数据
    sample_grades = [
        {
            'id': 1,
            'student_name': '张三',
            'student_no': '2021001',
            'course_code': 'CS101',
            'course_name': '计算机科学导论',
            'exam_name': '期中考试',
            'exam_type': 'midterm',
            'score': 85,
            'max_score': 100,
            'percentage': 85.0,
            'letter_grade': 'B',
            'is_published': True,
            'graded_at': '2024-01-15T10:30:00Z',
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'id': 2,
            'student_name': '李四',
            'student_no': '2021002',
            'course_code': 'CS101',
            'course_name': '计算机科学导论',
            'exam_name': '期中考试',
            'exam_type': 'midterm',
            'score': 92,
            'max_score': 100,
            'percentage': 92.0,
            'letter_grade': 'A',
            'is_published': True,
            'graded_at': '2024-01-15T10:30:00Z',
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'id': 3,
            'student_name': '王五',
            'student_no': '2021003',
            'course_code': 'MA201',
            'course_name': '高等数学',
            'exam_name': '期末考试',
            'exam_type': 'final',
            'score': 78,
            'max_score': 100,
            'percentage': 78.0,
            'letter_grade': 'C',
            'is_published': False,
            'graded_at': '2024-01-20T14:15:00Z',
            'created_at': '2024-01-20T14:15:00Z'
        }
    ]

    return jsonify({
        'success': True,
        'data': {
            'grades': sample_grades,
            'total': len(sample_grades),
            'page': 1,
            'pageSize': 20
        },
        'message': '获取成绩列表成功'
    })

@app.route('/api/teachers', methods=['GET', 'POST'])
def teachers():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'teachers': [],
                'total': 0,
                'page': 1,
                'pageSize': 20
            },
            'message': '获取教师列表成功'
        })
    else:  # POST
        return jsonify({
            'success': True,
            'message': '创建教师成功',
            'data': {
                'id': 1,
                'name': '新教师',
                'created_at': datetime.now().isoformat()
            }
        })

@app.route('/api/connection-test')
def connection_test():
    """连接测试接口"""
    return jsonify({
        'success': True,
        'message': '前后端连接测试成功！',
        'timestamp': datetime.now().isoformat(),
        'server': 'Flask Backend (Simplified)',
        'status': 'healthy',
        'data': {
            'backend_url': 'http://localhost:5000',
            'frontend_url': 'http://localhost:3001',
            'api_version': '1.0'
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("学生信息管理系统 - 简化登录服务")
    print("=" * 50)
    print("服务地址: http://localhost:5000")
    print("API端点: http://localhost:5000/api")
    print("")
    print("可用账号:")
    print("管理员: admin / 123456")
    print("学生: student / 123456")
    print("教师: teacher / 123456")
    print("=" * 50)

    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)