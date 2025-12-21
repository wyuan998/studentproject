# ========================================
# 学生信息管理系统 - 简化启动文件
# ========================================

import os
import json
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import logging
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入新的工具模块
try:
    from utils.file_handler import FileHandler
    from utils.privacy import PrivacyFilter, AuditLogger
except ImportError:
    print("Warning: 无法导入工具模块，将使用简化版功能")
    FileHandler = None
    PrivacyFilter = None

# 创建Flask应用
app = Flask(__name__)

# 配置JSON编码
app.config['JSON_AS_ASCII'] = False  # 确保中文字符正确编码
app.config['JSON_SORT_KEYS'] = False

# 配置CORS - 支持localhost:3000-3005并允许所有必要的方法和头
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
}, supports_credentials=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化文件处理器
if FileHandler:
    file_handler = FileHandler()

# 模拟数据存储
users = []
students = []
teachers = []
courses = []
grades = []
profile_history = []  # 个人信息变更历史

# 权限配置
ROLE_PERMISSIONS = {
    'admin': [
        'read', 'write', 'delete', 'manage_users', 'manage_courses',
        'manage_grades', 'system_settings', 'view_all_students', 'view_all_teachers',
        'view_all_courses', 'manage_system', 'export_data', 'import_data'
    ],
    'teacher': [
        'read', 'write', 'manage_own_courses', 'manage_grades', 'view_students',
        'view_assigned_courses', 'edit_own_profile', 'publish_grades'
    ],
    'student': [
        'read', 'view_own_grades', 'view_own_courses', 'edit_own_profile',
        'view_enrolled_courses', 'select_courses', 'drop_courses'
    ]
}

# 权限等级配置（用于权限比较）
ROLE_HIERARCHY = {
    'admin': 100,
    'teacher': 50,
    'student': 10
}

def get_role_permissions(role):
    """根据角色返回权限列表"""
    return ROLE_PERMISSIONS.get(role, ['read'])

def check_permission(user_role: str, required_permission: str) -> bool:
    """检查用户是否具有指定权限"""
    user_permissions = get_role_permissions(user_role)
    return required_permission in user_permissions

def check_role_hierarchy(user_role: str, required_role: str) -> bool:
    """检查用户角色等级是否满足要求"""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)

def require_permission(permission):
    """权限验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 在实际应用中，这里应该从JWT token中获取用户信息
            # 这里简化处理，从请求中获取用户信息
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'success': False,
                    'message': '缺少认证信息'
                }), 401

            # 模拟从token中解析用户信息
            # 在实际应用中，应该验证JWT token
            try:
                token = auth_header.replace('Bearer ', '')
                # 简化处理：根据token模拟用户角色
                if 'admin' in token.lower():
                    user_role = 'admin'
                elif 'teacher' in token.lower():
                    user_role = 'teacher'
                else:
                    user_role = 'student'
            except:
                return jsonify({
                    'success': False,
                    'message': '无效的认证信息'
                }), 401

            # 检查权限
            if not check_permission(user_role, permission):
                return jsonify({
                    'success': False,
                    'message': f'权限不足，需要权限: {permission}'
                }), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role):
    """角色验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 在实际应用中，这里应该从JWT token中获取用户信息
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'success': False,
                    'message': '缺少认证信息'
                }), 401

            # 模拟从token中解析用户角色
            try:
                token = auth_header.replace('Bearer ', '')
                if 'admin' in token.lower():
                    user_role = 'admin'
                elif 'teacher' in token.lower():
                    user_role = 'teacher'
                else:
                    user_role = 'student'
            except:
                return jsonify({
                    'success': False,
                    'message': '无效的认证信息'
                }), 401

            # 检查角色等级
            if not check_role_hierarchy(user_role, required_role):
                return jsonify({
                    'success': False,
                    'message': f'角色等级不足，需要角色: {required_role} 或更高'
                }), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator

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

        # 添加六个示例学生
        sample_students = [
            {
                'id': 1,
                'student_id': 'S2021001',
                'name': '张三',
                'gender': '男',
                'birth_date': '2000-01-01',
                'phone': '13800138001',
                'email': 'zhangsan@example.com',
                'username': 'zhangsan',
                'password': 'password123',
                'major': '计算机科学',
                'class_name': '计算机科学1班',
                'enrollment_date': '2021-09-01',
                'address': '北京市海淀区中关村大街1号',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            },
            {
                'id': 2,
                'student_id': 'S2021002',
                'name': '李四',
                'gender': '女',
                'birth_date': '2000-03-15',
                'phone': '13800138002',
                'email': 'lisi@example.com',
                'username': 'lisi',
                'password': 'password123',
                'major': '计算机科学',
                'class_name': '计算机科学1班',
                'enrollment_date': '2021-09-01',
                'address': '上海市浦东新区世纪大道100号',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            },
            {
                'id': 3,
                'student_id': 'S2021003',
                'name': '王五',
                'gender': '男',
                'birth_date': '2000-05-20',
                'phone': '13800138003',
                'email': 'wangwu@example.com',
                'username': 'wangwu',
                'password': 'password123',
                'major': '软件工程',
                'class_name': '软件工程2班',
                'enrollment_date': '2021-09-01',
                'address': '广州市天河区珠江新城核心区',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            },
            {
                'id': 4,
                'student_id': 'S2021004',
                'name': '赵六',
                'gender': '女',
                'birth_date': '2000-07-08',
                'phone': '13800138004',
                'email': 'zhaoliu@example.com',
                'username': 'zhaoliu',
                'password': 'password123',
                'major': '软件工程',
                'class_name': '软件工程2班',
                'enrollment_date': '2021-09-01',
                'address': '深圳市南山区科技园南区',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            },
            {
                'id': 5,
                'student_id': 'S2021005',
                'name': '陈七',
                'gender': '男',
                'birth_date': '2000-09-12',
                'phone': '13800138005',
                'email': 'chenqi@example.com',
                'username': 'chenqi',
                'password': 'password123',
                'major': '数据科学',
                'class_name': '数据科学1班',
                'enrollment_date': '2021-09-01',
                'address': '成都市高新区天府大道',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            },
            {
                'id': 6,
                'student_id': 'S2021006',
                'name': '刘八',
                'gender': '女',
                'birth_date': '2000-11-25',
                'phone': '13800138006',
                'email': 'liuba@example.com',
                'username': 'liuba',
                'password': 'password123',
                'major': '数据科学',
                'class_name': '数据科学1班',
                'enrollment_date': '2021-09-01',
                'address': '杭州市西湖区文三路',
                'status': 'active',
                'created_at': '2021-09-01T00:00:00'
            }
        ]

        # 将示例学生添加到列表中
        students.extend(sample_students)

        # 添加六个示例教师
        sample_teachers = [
            {
                'id': 1,
                'teacher_id': 'T0001',
                'name': '张教授',
                'username': 'zhangprof',
                'password': 'password123',
                'gender': '男',
                'birth_date': '1975-03-15',
                'phone': '13900001001',
                'email': 'zhang.prof@university.edu.cn',
                'department': '计算机科学系',
                'title': '教授',
                'hire_date': '2000-09-01',
                'address': '北京市海淀区清华大学',
                'status': 'active',
                'created_at': '2000-09-01T00:00:00'
            },
            {
                'id': 2,
                'teacher_id': 'T0002',
                'name': '李副教授',
                'username': 'liprof',
                'password': 'password123',
                'gender': '女',
                'birth_date': '1980-06-20',
                'phone': '13900001002',
                'email': 'li.prof@university.edu.cn',
                'department': '软件工程系',
                'title': '副教授',
                'hire_date': '2005-03-01',
                'address': '上海市闵行区上海交通大学',
                'status': 'active',
                'created_at': '2005-03-01T00:00:00'
            },
            {
                'id': 3,
                'teacher_id': 'T0003',
                'name': '王讲师',
                'username': 'wanglec',
                'password': 'password123',
                'gender': '男',
                'birth_date': '1985-09-10',
                'phone': '13900001003',
                'email': 'wang.lec@university.edu.cn',
                'department': '数据科学系',
                'title': '讲师',
                'hire_date': '2010-09-01',
                'address': '广州市番禺区中山大学',
                'status': 'active',
                'created_at': '2010-09-01T00:00:00'
            },
            {
                'id': 4,
                'teacher_id': 'T0004',
                'name': '陈助教',
                'username': 'chenassist',
                'password': 'password123',
                'gender': '女',
                'birth_date': '1990-12-05',
                'phone': '13900001004',
                'email': 'chen.assist@university.edu.cn',
                'department': '电子工程系',
                'title': '助教',
                'hire_date': '2018-03-01',
                'address': '深圳市南山区深圳大学',
                'status': 'active',
                'created_at': '2018-03-01T00:00:00'
            },
            {
                'id': 5,
                'teacher_id': 'T0005',
                'name': '刘教授',
                'username': 'liuprof',
                'password': 'password123',
                'gender': '男',
                'birth_date': '1972-04-25',
                'phone': '13900001005',
                'email': 'liu.prof@university.edu.cn',
                'department': '数学系',
                'title': '教授',
                'hire_date': '1998-09-01',
                'address': '杭州市西湖区浙江大学',
                'status': 'active',
                'created_at': '1998-09-01T00:00:00'
            },
            {
                'id': 6,
                'teacher_id': 'T0006',
                'name': '赵副教授',
                'username': 'zhaoprof',
                'password': 'password123',
                'gender': '女',
                'birth_date': '1978-07-18',
                'phone': '13900001006',
                'email': 'zhao.prof@university.edu.cn',
                'department': '物理系',
                'title': '副教授',
                'hire_date': '2003-09-01',
                'address': '武汉市洪山区武汉大学',
                'status': 'active',
                'created_at': '2003-09-01T00:00:00'
            }
        ]

        # 将示例教师添加到列表中
        teachers.extend(sample_teachers)

        # 将学生和教师账号添加到users列表中以便登录
        for student in sample_students:
            users.append({
                'id': student['id'],
                'username': student['username'],
                'password': student['password'],
                'real_name': student['name'],
                'email': student['email'],
                'role': 'student',
                'created_at': student['created_at'],
                'status': 'active'
            })

        for teacher in sample_teachers:
            users.append({
                'id': teacher['id'] + 100,  # 避免ID冲突
                'username': teacher['username'],
                'password': teacher['password'],
                'real_name': teacher['name'],
                'email': teacher['email'],
                'role': 'teacher',
                'created_at': teacher['created_at'],
                'status': 'active'
            })

        # 添加六个示例课程
        sample_courses = [
            {
                'id': 1,
                'course_code': 'CS101',
                'course_name': '计算机科学导论',
                'credits': 3,
                'hours': 48,
                'course_type': 'required',
                'teacher_id': 1,
                'teacher_name': '张教授',
                'department': '计算机科学系',
                'semester': '2025-春季',
                'max_students': 50,
                'current_students': 25,
                'status': 'active',
                'schedule': '周一 14:00-16:00',
                'location': '教学楼A201',
                'description': '计算机科学基础课程，涵盖计算机基本概念、编程入门等内容。',
                'created_at': '2025-01-01T00:00:00'
            },
            {
                'id': 2,
                'course_code': 'SE201',
                'course_name': '软件工程',
                'credits': 4,
                'hours': 64,
                'course_type': 'required',
                'teacher_id': 2,
                'teacher_name': '李副教授',
                'department': '软件工程系',
                'semester': '2025-春季',
                'max_students': 40,
                'current_students': 38,
                'status': 'active',
                'schedule': '周二、周四 10:00-12:00',
                'location': '实验楼B305',
                'description': '软件工程理论与实践，包括软件开发生命周期、项目管理等内容。',
                'created_at': '2025-01-01T00:00:00'
            },
            {
                'id': 3,
                'course_code': 'DS301',
                'course_name': '数据结构与算法',
                'credits': 4,
                'hours': 64,
                'course_type': 'required',
                'teacher_id': 3,
                'teacher_name': '王讲师',
                'department': '数据科学系',
                'semester': '2025-春季',
                'max_students': 35,
                'current_students': 30,
                'status': 'active',
                'schedule': '周三、周五 14:00-16:00',
                'location': '教学楼C102',
                'description': '深入学习数据结构和算法，包括排序、搜索、图算法等。',
                'created_at': '2025-01-01T00:00:00'
            },
            {
                'id': 4,
                'course_code': 'AI401',
                'course_name': '人工智能导论',
                'credits': 3,
                'hours': 48,
                'course_type': 'elective',
                'teacher_id': 5,
                'teacher_name': '刘教授',
                'department': '数学系',
                'semester': '2024-秋季',
                'max_students': 30,
                'current_students': 15,
                'status': 'active',
                'schedule': '周一 18:00-20:00',
                'location': '教学楼D203',
                'description': '人工智能基础概念，包括机器学习、深度学习、自然语言处理等。',
                'created_at': '2024-09-01T00:00:00'
            },
            {
                'id': 5,
                'course_code': 'DB201',
                'course_name': '数据库系统',
                'credits': 3,
                'hours': 48,
                'course_type': 'required',
                'teacher_id': 4,
                'teacher_name': '陈助教',
                'department': '电子工程系',
                'semester': '2024-秋季',
                'max_students': 40,
                'current_students': 40,
                'status': 'full',
                'schedule': '周二、周四 14:00-16:00',
                'location': '实验楼E401',
                'description': '关系型数据库设计、SQL语言、NoSQL数据库等内容。',
                'created_at': '2024-09-01T00:00:00'
            },
            {
                'id': 6,
                'course_code': 'ML501',
                'course_name': '机器学习',
                'credits': 4,
                'hours': 64,
                'course_type': 'elective',
                'teacher_id': 6,
                'teacher_name': '赵副教授',
                'department': '物理系',
                'semester': '2024-夏季',
                'max_students': 25,
                'current_students': 18,
                'status': 'suspended',
                'schedule': '周一、周三、周五 16:00-18:00',
                'location': '教学楼F101',
                'description': '机器学习算法原理与实践，包括监督学习、无监督学习等。',
                'created_at': '2024-06-01T00:00:00'
            }
        ]

        # 将示例课程添加到列表中
        courses.extend(sample_courses)

        # 添加示例成绩数据
        sample_grades = [
            # 张三的成绩
            {
                'id': 1,
                'student_id': 1,  # 张三
                'course_id': 1,   # CS101
                'exam_type': 'midterm',
                'exam_name': '期中考试',
                'score': 85,
                'max_score': 100,
                'weight': 0.3,
                'semester': '2025-春季',
                'is_published': True,
                'is_locked': False,
                'graded_by': 1,  # 授课教师
                'graded_at': '2025-03-15T10:00:00',
                'published_at': '2025-03-16T09:00:00',
                'comments': '基础知识掌握扎实，但在实际应用方面需要加强。',
                'class_average': 78.5,
                'class_max': 95,
                'class_min': 65,
                'percentage': 85.0,
                'letter_grade': 'B+',
                'grade_point': 3.3,
                'created_at': '2025-03-15T10:00:00'
            },
            {
                'id': 2,
                'student_id': 1,
                'course_id': 1,
                'exam_type': 'final',
                'exam_name': '期末考试',
                'score': 88,
                'max_score': 100,
                'weight': 0.4,
                'semester': '2025-春季',
                'is_published': True,
                'is_locked': False,
                'graded_by': 1,
                'graded_at': '2025-04-20T14:00:00',
                'published_at': '2025-04-21T09:00:00',
                'comments': '期末表现良好，综合能力有所提升。',
                'class_average': 76.3,
                'class_max': 98,
                'class_min': 52,
                'percentage': 88.0,
                'letter_grade': 'A-',
                'grade_point': 3.7,
                'created_at': '2025-04-20T14:00:00'
            },
            # 李四的成绩
            {
                'id': 3,
                'student_id': 2,  # 李四
                'course_id': 1,
                'exam_type': 'midterm',
                'exam_name': '期中考试',
                'score': 92,
                'max_score': 100,
                'weight': 0.3,
                'semester': '2025-春季',
                'is_published': True,
                'is_locked': False,
                'graded_by': 1,
                'graded_at': '2025-03-15T10:00:00',
                'published_at': '2025-03-16T09:00:00',
                'comments': '成绩优秀，逻辑思维清晰。',
                'class_average': 78.5,
                'class_max': 95,
                'class_min': 65,
                'percentage': 92.0,
                'letter_grade': 'A',
                'grade_point': 4.0,
                'created_at': '2025-03-15T10:00:00'
            },
            {
                'id': 4,
                'student_id': 2,
                'course_id': 2,  # SE201
                'exam_type': 'assignment',
                'exam_name': '作业1',
                'score': 95,
                'max_score': 100,
                'weight': 0.1,
                'semester': '2025-春季',
                'is_published': True,
                'is_locked': False,
                'graded_by': 2,
                'graded_at': '2025-03-10T16:00:00',
                'published_at': '2025-03-11T09:00:00',
                'comments': '作业完成质量很高，代码规范性强。',
                'class_average': 82.1,
                'class_max': 100,
                'class_min': 45,
                'percentage': 95.0,
                'letter_grade': 'A',
                'grade_point': 4.0,
                'created_at': '2025-03-10T16:00:00'
            },
            # 王五的成绩
            {
                'id': 5,
                'student_id': 3,  # 王五
                'course_id': 2,
                'exam_type': 'quiz',
                'exam_name': '第1次测验',
                'score': 76,
                'max_score': 100,
                'weight': 0.15,
                'semester': '2025-春季',
                'is_published': False,
                'is_locked': False,
                'graded_by': 2,
                'graded_at': '2025-03-05T15:30:00',
                'comments': '基础概念理解尚可，但应用能力需要提升。',
                'class_average': 73.2,
                'class_max': 92,
                'class_min': 58,
                'percentage': 76.0,
                'letter_grade': 'B',
                'grade_point': 3.0,
                'created_at': '2025-03-05T15:30:00'
            },
            {
                'id': 6,
                'student_id': 3,
                'course_id': 3,  # DS301
                'exam_type': 'project',
                'exam_name': '数据结构项目',
                'score': 82,
                'max_score': 100,
                'weight': 0.25,
                'semester': '2025-春季',
                'is_published': True,
                'is_locked': False,
                'graded_by': 3,
                'graded_at': '2025-04-10T17:00:00',
                'published_at': '2025-04-11T09:00:00',
                'comments': '项目完成情况良好，算法设计思路清晰。',
                'class_average': 77.8,
                'class_max': 96,
                'class_min': 62,
                'percentage': 82.0,
                'letter_grade': 'B+',
                'grade_point': 3.3,
                'created_at': '2025-04-10T17:00:00'
            }
        ]

        grades.extend(sample_grades)

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
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试手动解析数据
            raw_data = request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        # 简单的用户验证（实际应用中应该更安全）
        user = None
        for u in users:
            if u['username'] == username and u['password'] == password:
                user = u
                break

        if user:
            # 根据角色设置不同的权限
            role = user.get('role', 'student')
            permissions = get_role_permissions(role)

            # 构建响应数据
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'real_name': user.get('real_name', user['username']),
                'email': user.get('email', ''),
                'role': role,
                'permissions': permissions,
                'roles': [role]
            }

            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'access_token': 'mock-jwt-token-' + str(user['id']),
                    'refresh_token': 'mock-refresh-token-' + str(user['id']),
                    'user_info': user_data
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
    except Exception as e:
        logger.error(f"登录错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器处理错误'
        }), 500

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    """用户注册"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试手动解析数据
            raw_data = request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        # 获取注册信息
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        phone = data.get('phone')
        real_name = data.get('real_name')
        student_id = data.get('student_id')

        # 验证必填字段
        if not all([username, email, password, confirm_password, real_name]):
            return jsonify({
                'success': False,
                'message': '请填写所有必填字段'
            }), 400

        # 验证密码匹配
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': '两次输入的密码不一致'
            }), 400

        # 验证密码长度
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': '密码长度至少为6位'
            }), 400

        # 验证用户名长度
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': '用户名长度至少为3位'
            }), 400

        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'message': '请输入有效的邮箱地址'
            }), 400

        # 验证手机号格式
        if phone:
            phone_pattern = r'^1[3-9]\d{9}$'
            if not re.match(phone_pattern, phone):
                return jsonify({
                    'success': False,
                    'message': '请输入有效的手机号'
                }), 400

        # 检查用户名是否已存在
        for u in users:
            if u['username'] == username:
                return jsonify({
                    'success': False,
                    'message': '用户名已存在'
                }), 400

        # 检查邮箱是否已存在
        for u in users:
            if u.get('email') == email:
                return jsonify({
                    'success': False,
                    'message': '邮箱已被注册'
                }), 400

        # 检查学号是否已存在
        if student_id:
            for s in students:
                if s.get('student_id') == student_id:
                    return jsonify({
                        'success': False,
                        'message': '学号已存在'
                    }), 400

        # 创建新用户（作为学生角色）
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': password,  # 实际应用中应该加密存储
            'real_name': real_name,
            'email': email,
            'phone': phone,
            'role': 'student',  # 注册用户默认为学生角色
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        # 将用户添加到用户列表
        users.append(new_user)

        # 如果提供了学号信息，同时添加到学生列表
        if student_id:
            # 检查该学号是否已存在
            student_exists = False
            for s in students:
                if s.get('student_id') == student_id:
                    student_exists = True
                    break

            if not student_exists:
                new_student = {
                    'id': len(students) + 1,
                    'student_id': student_id,
                    'name': real_name,
                    'gender': '',  # 可以后续完善
                    'birth_date': '',
                    'phone': phone,
                    'email': email,
                    'username': username,
                    'password': password,
                    'major': '',  # 可以后续完善
                    'class_name': '',  # 可以后续完善
                    'enrollment_date': datetime.now().strftime('%Y-%m-%d'),
                    'address': '',
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                }
                students.append(new_student)

        logger.info(f"成功注册用户: {username}")

        return jsonify({
            'success': True,
            'message': '注册成功！',
            'data': {
                'user': {
                    'id': new_user['id'],
                    'username': new_user['username'],
                    'real_name': new_user['real_name'],
                    'email': new_user['email'],
                    'role': new_user['role']
                }
            }
        })

    except Exception as e:
        logger.error(f"注册错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '注册失败，请稍后重试'
        }), 500

@app.route('/api/auth/check-username', methods=['GET'])
def check_username():
    """检查用户名是否可用"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({
                'success': False,
                'message': '缺少用户名参数'
            }), 400

        # 检查用户名是否已存在
        for u in users:
            if u['username'] == username:
                return jsonify({
                    'success': False,
                    'message': '用户名已存在'
                })

        return jsonify({
            'success': True,
            'message': '用户名可用'
        })

    except Exception as e:
        logger.error(f"检查用户名错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '检查失败'
        }), 500

@app.route('/api/auth/check-email', methods=['GET'])
def check_email():
    """检查邮箱是否可用"""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({
                'success': False,
                'message': '缺少邮箱参数'
            }), 400

        # 检查邮箱是否已存在
        for u in users:
            if u.get('email') == email:
                return jsonify({
                    'success': False,
                    'message': '邮箱已被注册'
                })

        return jsonify({
            'success': True,
            'message': '邮箱可用'
        })

    except Exception as e:
        logger.error(f"检查邮箱错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '检查失败'
        }), 500

# 学生管理路由
@app.route('/api/students', methods=['GET', 'OPTIONS'])
def get_students():
    """获取学生列表"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 权限检查 - 获取学生列表需要相应权限
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # 如果有认证信息，检查权限
        if 'admin' in auth_header:
            required_permission = 'view_all_students'
        elif 'teacher' in auth_header:
            required_permission = 'view_students'
        else:
            required_permission = 'read'

        try:
            token = auth_header.replace('Bearer ', '')
            if 'admin' in token.lower():
                user_role = 'admin'
            elif 'teacher' in token.lower():
                user_role = 'teacher'
            else:
                user_role = 'student'

            if not check_permission(user_role, required_permission):
                return jsonify({
                    'success': False,
                    'message': f'权限不足，需要权限: {required_permission}'
                }), 403
        except:
            pass  # 如果token解析失败，继续执行（允许公开访问基础信息）

    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        keyword = request.args.get('keyword', '')

        logger.info(f"获取学生列表 - 关键词: {keyword}, 页码: {page}")

        # 简单的过滤逻辑
        filtered_students = students
        if keyword:
            filtered_students = [s for s in students
                              if keyword.lower() in s.get('name', '').lower()
                              or keyword.lower() in s.get('student_id', '').lower()]

        response_data = {
            'success': True,
            'data': {
                'students': filtered_students,
                'total': len(filtered_students),
                'page': page,
                'pageSize': page_size
            }
        }

        logger.info(f"返回 {len(filtered_students)} 条学生记录")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"获取学生列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取学生列表失败'
        }), 500

@app.route('/api/students', methods=['POST'])
def create_student():
    """创建学生"""
    # 权限检查 - 创建学生需要管理员权限
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin' not in auth_header:
        return jsonify({
            'success': False,
            'message': '权限不足，只有管理员可以创建学生'
        }), 403

    try:
        logger.info("收到创建学生请求")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试手动解析数据
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的学生数据: {data}")

        # 验证必填字段
        required_fields = ['student_id', 'name', 'gender', 'major', 'class_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 检查学号是否已存在
        for student in students:
            if student.get('student_id') == data.get('student_id'):
                return jsonify({
                    'success': False,
                    'message': '学号已存在'
                }), 400

        new_student = {
            'id': len(students) + 1,
            'student_id': data.get('student_id'),
            'name': data.get('name'),
            'gender': data.get('gender'),
            'birth_date': data.get('birth_date', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'username': data.get('username', ''),
            'password': data.get('password', ''),
            'major': data.get('major'),
            'class_name': data.get('class_name'),
            'enrollment_date': data.get('enrollment_date', ''),
            'address': data.get('address', ''),
            'status': data.get('status', 'active'),
            'created_at': datetime.now().isoformat()
        }

        students.append(new_student)
        logger.info(f"成功创建学生: {new_student['name']}")

        return jsonify({
            'success': True,
            'message': '学生创建成功',
            'data': new_student
        })

    except Exception as e:
        logger.error(f"创建学生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建学生失败: {str(e)}'
        }), 500

@app.route('/api/students/<int:student_id>', methods=['PUT', 'OPTIONS'])
def update_student(student_id):
    """更新学生信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到更新学生请求: ID={student_id}")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始更新数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的更新数据: {data}")

        # 查找学生
        student_index = -1
        for i, student in enumerate(students):
            if student.get('id') == student_id:
                student_index = i
                break

        if student_index == -1:
            return jsonify({
                'success': False,
                'message': '学生不存在'
            }), 404

        # 更新学生信息
        updated_student = students[student_index].copy()
        updated_student.update({
            'student_id': data.get('student_id', updated_student.get('student_id')),
            'name': data.get('name', updated_student.get('name')),
            'gender': data.get('gender', updated_student.get('gender')),
            'birth_date': data.get('birth_date', updated_student.get('birth_date')),
            'phone': data.get('phone', updated_student.get('phone')),
            'email': data.get('email', updated_student.get('email')),
            'username': data.get('username', updated_student.get('username')),
            'password': data.get('password', updated_student.get('password')),
            'major': data.get('major', updated_student.get('major')),
            'class_name': data.get('class_name', updated_student.get('class_name')),
            'enrollment_date': data.get('enrollment_date', updated_student.get('enrollment_date')),
            'address': data.get('address', updated_student.get('address')),
            'status': data.get('status', updated_student.get('status')),
            'updated_at': datetime.now().isoformat()
        })

        students[student_index] = updated_student
        logger.info(f"成功更新学生: {updated_student['name']}")

        return jsonify({
            'success': True,
            'message': '学生信息更新成功',
            'data': updated_student
        })

    except Exception as e:
        logger.error(f"更新学生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新学生失败: {str(e)}'
        }), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE', 'OPTIONS'])
def delete_student(student_id):
    """删除学生"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到删除学生请求: ID={student_id}")

        # 查找学生
        student_index = -1
        for i, student in enumerate(students):
            if student.get('id') == student_id:
                student_index = i
                break

        if student_index == -1:
            return jsonify({
                'success': False,
                'message': '学生不存在'
            }), 404

        deleted_student = students.pop(student_index)
        logger.info(f"成功删除学生: {deleted_student['name']}")

        return jsonify({
            'success': True,
            'message': '学生删除成功',
            'data': deleted_student
        })

    except Exception as e:
        logger.error(f"删除学生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除学生失败: {str(e)}'
        }), 500

# 教师管理路由
@app.route('/api/teachers', methods=['GET', 'OPTIONS'])
def get_teachers():
    """获取教师列表"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        keyword = request.args.get('keyword', '')
        department = request.args.get('department', '')
        title = request.args.get('title', '')

        logger.info(f"获取教师列表 - 关键词: {keyword}, 院系: {department}, 职称: {title}, 页码: {page}")

        # 简单的过滤逻辑
        filtered_teachers = teachers
        if keyword:
            filtered_teachers = [t for t in teachers
                              if keyword.lower() in t.get('name', '').lower()
                              or keyword.lower() in t.get('teacher_id', '').lower()
                              or keyword.lower() in t.get('department', '').lower()]

        if department:
            filtered_teachers = [t for t in filtered_teachers
                               if t.get('department', '') == department]

        if title:
            filtered_teachers = [t for t in filtered_teachers
                               if t.get('title', '') == title]

        response_data = {
            'success': True,
            'data': {
                'teachers': filtered_teachers,
                'total': len(filtered_teachers),
                'page': page,
                'pageSize': page_size
            }
        }

        logger.info(f"返回 {len(filtered_teachers)} 条教师记录")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"获取教师列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取教师列表失败'
        }), 500

@app.route('/api/teachers', methods=['POST'])
def create_teacher():
    """创建教师"""
    # 权限检查 - 创建教师需要管理员权限
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin' not in auth_header:
        return jsonify({
            'success': False,
            'message': '权限不足，只有管理员可以创建教师'
        }), 403

    try:
        logger.info("收到创建教师请求")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试手动解析数据
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的教师数据: {data}")

        # 验证必填字段
        required_fields = ['teacher_id', 'name', 'gender', 'department', 'title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 检查工号是否已存在
        for teacher in teachers:
            if teacher.get('teacher_id') == data.get('teacher_id'):
                return jsonify({
                    'success': False,
                    'message': '工号已存在'
                }), 400

        new_teacher = {
            'id': len(teachers) + 1,
            'teacher_id': data.get('teacher_id'),
            'name': data.get('name'),
            'gender': data.get('gender'),
            'birth_date': data.get('birth_date', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'username': data.get('username', ''),
            'password': data.get('password', ''),
            'department': data.get('department'),
            'title': data.get('title'),
            'hire_date': data.get('hire_date', ''),
            'address': data.get('address', ''),
            'status': data.get('status', 'active'),
            'created_at': datetime.now().isoformat()
        }

        teachers.append(new_teacher)
        logger.info(f"成功创建教师: {new_teacher['name']}")

        return jsonify({
            'success': True,
            'message': '教师创建成功',
            'data': new_teacher
        })

    except Exception as e:
        logger.error(f"创建教师错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建教师失败: {str(e)}'
        }), 500

@app.route('/api/teachers/<int:teacher_id>', methods=['PUT', 'OPTIONS'])
def update_teacher(teacher_id):
    """更新教师信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到更新教师请求: ID={teacher_id}")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始更新数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的更新数据: {data}")

        # 查找教师
        teacher_index = -1
        for i, teacher in enumerate(teachers):
            if teacher.get('id') == teacher_id:
                teacher_index = i
                break

        if teacher_index == -1:
            return jsonify({
                'success': False,
                'message': '教师不存在'
            }), 404

        # 更新教师信息
        updated_teacher = teachers[teacher_index].copy()
        updated_teacher.update({
            'teacher_id': data.get('teacher_id', updated_teacher.get('teacher_id')),
            'name': data.get('name', updated_teacher.get('name')),
            'gender': data.get('gender', updated_teacher.get('gender')),
            'birth_date': data.get('birth_date', updated_teacher.get('birth_date')),
            'phone': data.get('phone', updated_teacher.get('phone')),
            'email': data.get('email', updated_teacher.get('email')),
            'username': data.get('username', updated_teacher.get('username')),
            'password': data.get('password', updated_teacher.get('password')),
            'department': data.get('department', updated_teacher.get('department')),
            'title': data.get('title', updated_teacher.get('title')),
            'hire_date': data.get('hire_date', updated_teacher.get('hire_date')),
            'address': data.get('address', updated_teacher.get('address')),
            'status': data.get('status', updated_teacher.get('status')),
            'updated_at': datetime.now().isoformat()
        })

        teachers[teacher_index] = updated_teacher
        logger.info(f"成功更新教师: {updated_teacher['name']}")

        return jsonify({
            'success': True,
            'message': '教师信息更新成功',
            'data': updated_teacher
        })

    except Exception as e:
        logger.error(f"更新教师错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新教师失败: {str(e)}'
        }), 500

@app.route('/api/teachers/<int:teacher_id>', methods=['DELETE', 'OPTIONS'])
def delete_teacher(teacher_id):
    """删除教师"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到删除教师请求: ID={teacher_id}")

        # 查找教师
        teacher_index = -1
        for i, teacher in enumerate(teachers):
            if teacher.get('id') == teacher_id:
                teacher_index = i
                break

        if teacher_index == -1:
            return jsonify({
                'success': False,
                'message': '教师不存在'
            }), 404

        deleted_teacher = teachers.pop(teacher_index)
        logger.info(f"成功删除教师: {deleted_teacher['name']}")

        return jsonify({
            'success': True,
            'message': '教师删除成功',
            'data': deleted_teacher
        })

    except Exception as e:
        logger.error(f"删除教师错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除教师失败: {str(e)}'
        }), 500

# 课程管理路由
@app.route('/api/courses', methods=['GET', 'OPTIONS'])
def get_courses():
    """获取课程列表"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        keyword = request.args.get('keyword', '')
        semester = request.args.get('semester', '')
        department = request.args.get('department', '')

        logger.info(f"获取课程列表 - 关键词: {keyword}, 学期: {semester}, 院系: {department}, 页码: {page}")

        # 简单的过滤逻辑
        filtered_courses = courses
        if keyword:
            filtered_courses = [c for c in courses
                              if keyword.lower() in c.get('course_name', '').lower()
                              or keyword.lower() in c.get('course_code', '').lower()
                              or keyword.lower() in c.get('teacher_name', '').lower()
                              or keyword.lower() in c.get('department', '').lower()]

        if semester:
            filtered_courses = [c for c in filtered_courses
                               if c.get('semester', '') == semester]

        if department:
            filtered_courses = [c for c in filtered_courses
                               if c.get('department', '') == department]

        response_data = {
            'success': True,
            'data': {
                'courses': filtered_courses,
                'total': len(filtered_courses),
                'page': page,
                'pageSize': page_size
            }
        }

        logger.info(f"返回 {len(filtered_courses)} 条课程记录")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"获取课程列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取课程列表失败'
        }), 500

@app.route('/api/courses', methods=['POST'])
def create_course():
    """创建课程"""
    try:
        logger.info("收到创建课程请求")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试手动解析数据
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的课程数据: {data}")

        # 验证必填字段
        required_fields = ['course_code', 'course_name', 'credits', 'teacher_name', 'teacher_id', 'department', 'semester']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 验证数值范围
        if data.get('credits', 0) < 1 or data.get('credits', 0) > 10:
            return jsonify({
                'success': False,
                'message': '学分必须在1到10之间'
            }), 400

        if data.get('hours', 0) < 1 or data.get('hours', 0) > 200:
            return jsonify({
                'success': False,
                'message': '学时必须在1到200之间'
            }), 400

        if data.get('max_students', 0) < 1 or data.get('max_students', 0) > 500:
            return jsonify({
                'success': False,
                'message': '最大人数必须在1到500之间'
            }), 400

        # 检查当前人数是否超过最大人数
        if data.get('current_students', 0) > data.get('max_students', 0):
            return jsonify({
                'success': False,
                'message': '当前人数不能超过最大人数'
            }), 400

        # 检查课程代码是否已存在
        for course in courses:
            if course.get('course_code') == data.get('course_code'):
                return jsonify({
                    'success': False,
                    'message': '课程代码已存在'
                }), 400

        new_course = {
            'id': len(courses) + 1,
            'course_code': data.get('course_code'),
            'course_name': data.get('course_name'),
            'credits': data.get('credits'),
            'hours': data.get('hours'),
            'course_type': data.get('course_type', ''),
            'teacher_id': data.get('teacher_id'),
            'teacher_name': data.get('teacher_name'),
            'department': data.get('department'),
            'semester': data.get('semester'),
            'max_students': data.get('max_students'),
            'current_students': data.get('current_students', 0),
            'status': data.get('status', 'active'),
            'schedule': data.get('schedule', ''),
            'location': data.get('location', ''),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat()
        }

        courses.append(new_course)
        logger.info(f"成功创建课程: {new_course['course_name']}")

        return jsonify({
            'success': True,
            'message': '课程创建成功',
            'data': new_course
        })

    except Exception as e:
        logger.error(f"创建课程错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建课程失败: {str(e)}'
        }), 500

@app.route('/api/courses/<int:course_id>', methods=['PUT', 'OPTIONS'])
def update_course(course_id):
    """更新课程信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到更新课程请求: ID={course_id}")

        # 确保正确解析JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.get_data(as_text=True)
            logger.info(f"原始更新数据: {raw_data}")
            if raw_data:
                data = json.loads(raw_data)
            else:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400

        logger.info(f"解析的更新数据: {data}")

        # 查找课程
        course_index = -1
        for i, course in enumerate(courses):
            if course.get('id') == course_id:
                course_index = i
                break

        if course_index == -1:
            return jsonify({
                'success': False,
                'message': '课程不存在'
            }), 404

        # 更新课程信息
        updated_course = courses[course_index].copy()
        updated_course.update({
            'course_code': data.get('course_code', updated_course.get('course_code')),
            'course_name': data.get('course_name', updated_course.get('course_name')),
            'credits': data.get('credits', updated_course.get('credits')),
            'hours': data.get('hours', updated_course.get('hours')),
            'course_type': data.get('course_type', updated_course.get('course_type')),
            'teacher_id': data.get('teacher_id', updated_course.get('teacher_id')),
            'teacher_name': data.get('teacher_name', updated_course.get('teacher_name')),
            'department': data.get('department', updated_course.get('department')),
            'semester': data.get('semester', updated_course.get('semester')),
            'max_students': data.get('max_students', updated_course.get('max_students')),
            'current_students': data.get('current_students', updated_course.get('current_students')),
            'status': data.get('status', updated_course.get('status')),
            'schedule': data.get('schedule', updated_course.get('schedule')),
            'location': data.get('location', updated_course.get('location')),
            'description': data.get('description', updated_course.get('description')),
            'updated_at': datetime.now().isoformat()
        })

        # 验证数值范围
        if updated_course['credits'] < 1 or updated_course['credits'] > 10:
            return jsonify({
                'success': False,
                'message': '学分必须在1到10之间'
            }), 400

        if updated_course['hours'] < 1 or updated_course['hours'] > 200:
            return jsonify({
                'success': False,
                'message': '学时必须在1到200之间'
            }), 400

        if updated_course['max_students'] < 1 or updated_course['max_students'] > 500:
            return jsonify({
                'success': False,
                'message': '最大人数必须在1到500之间'
            }), 400

        if updated_course['current_students'] > updated_course['max_students']:
            return jsonify({
                'success': False,
                'message': '当前人数不能超过最大人数'
            }), 400

        courses[course_index] = updated_course
        logger.info(f"成功更新课程: {updated_course['course_name']}")

        return jsonify({
            'success': True,
            'message': '课程信息更新成功',
            'data': updated_course
        })

    except Exception as e:
        logger.error(f"更新课程错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新课程失败: {str(e)}'
        }), 500

@app.route('/api/courses/<int:course_id>', methods=['DELETE', 'OPTIONS'])
def delete_course(course_id):
    """删除课程"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        logger.info(f"收到删除课程请求: ID={course_id}")

        # 查找课程
        course_index = -1
        for i, course in enumerate(courses):
            if course.get('id') == course_id:
                course_index = i
                break

        if course_index == -1:
            return jsonify({
                'success': False,
                'message': '课程不存在'
            }), 404

        deleted_course = courses.pop(course_index)
        logger.info(f"成功删除课程: {deleted_course['course_name']}")

        return jsonify({
            'success': True,
            'message': '课程删除成功',
            'data': deleted_course
        })

    except Exception as e:
        logger.error(f"删除课程错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除课程失败: {str(e)}'
        }), 500

# 成绩管理路由
@app.route('/api/grades', methods=['GET'])
def get_grades():
    """获取成绩列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        keyword = request.args.get('keyword', '')
        course_id = request.args.get('course_id', '')
        exam_type = request.args.get('exam_type', '')
        semester = request.args.get('semester', '')
        is_published = request.args.get('is_published')

        # 过滤成绩
        filtered_grades = grades.copy()

        if keyword:
            keyword_lower = keyword.lower()
            filtered_grades = [g for g in filtered_grades
                if (any(str(student.get('name', '')).lower() for student in students if student.get('id') == g.get('student_id')) and keyword_lower in str(student.get('name', '')).lower())
                or (any(str(student.get('student_id', '')).lower() for student in students if student.get('id') == g.get('student_id')) and keyword_lower in str(student.get('student_id', '')).lower())
                or (any(str(course.get('course_name', '')).lower() for course in courses if course.get('id') == g.get('course_id')) and keyword_lower in str(course.get('course_name', '')).lower())
                or (any(str(course.get('course_code', '')).lower() for course in courses if course.get('id') == g.get('course_id')) and keyword_lower in str(course.get('course_code', '')).lower())]

        if course_id:
            filtered_grades = [g for g in filtered_grades if str(g.get('course_id')) == str(course_id)]

        if exam_type:
            filtered_grades = [g for g in filtered_grades if g.get('exam_type') == exam_type]

        if semester:
            filtered_grades = [g for g in filtered_grades if semester in g.get('semester', '')]

        if is_published is not None:
            is_published_bool = is_published.lower() == 'true'
            filtered_grades = [g for g in filtered_grades if g.get('is_published') == is_published_bool]

        # 分页
        total = len(filtered_grades)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_grades = filtered_grades[start_idx:end_idx]

        # 补充关联数据
        for grade in page_grades:
            # 添加学生信息
            student = next((s for s in students if s.get('id') == grade.get('student_id')), {})
            grade['student_name'] = student.get('name', '')
            grade['student_no'] = student.get('student_id', '')
            # 保留原始的student_id作为关联ID

            # 添加课程信息
            course = next((c for c in courses if c.get('id') == grade.get('course_id')), {})
            grade['course_name'] = course.get('course_name', '')
            grade['course_code'] = course.get('course_code', '')

        return jsonify({
            'success': True,
            'data': {
                'grades': page_grades,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"获取成绩列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取成绩列表失败: {str(e)}'
        }), 500

@app.route('/api/grades', methods=['POST'])
def create_grade():
    """创建成绩记录"""
    try:
        data = request.get_json()
        logger.info(f"收到创建成绩请求: {data}")

        # 验证必填字段
        required_fields = ['student_id', 'course_id', 'exam_type', 'exam_name', 'score', 'semester']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 验证分数
        score = float(data['score'])
        max_score = float(data.get('max_score', 100))
        if score < 0 or score > max_score:
            return jsonify({
                'success': False,
                'message': f'分数必须在0-{max_score}之间'
            }), 400

        # 创建新成绩
        new_grade = {
            'id': len(grades) + 1,
            'student_id': data['student_id'],
            'course_id': data['course_id'],
            'exam_type': data['exam_type'],
            'exam_name': data['exam_name'],
            'score': score,
            'max_score': max_score,
            'weight': float(data.get('weight', 1.0)),
            'semester': data['semester'],
            'is_published': data.get('is_published', False),
            'is_locked': False,
            'graded_by': 1,  # 假设当前用户ID为1
            'graded_at': datetime.now().isoformat(),
            'comments': data.get('comments', ''),
            'improvement_suggestions': data.get('improvement_suggestions', ''),
            'percentage': (score / max_score) * 100,
            'letter_grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F',
            'grade_point': 4.0 if score >= 90 else 3.0 if score >= 80 else 2.0 if score >= 70 else 1.0 if score >= 60 else 0.0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        grades.append(new_grade)
        logger.info(f"成功创建成绩: {new_grade['exam_name']}")

        return jsonify({
            'success': True,
            'message': '成绩创建成功',
            'data': new_grade
        })

    except Exception as e:
        logger.error(f"创建成绩错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建成绩失败: {str(e)}'
        }), 500

@app.route('/api/grades/<int:grade_id>', methods=['PUT'])
def update_grade(grade_id):
    """更新成绩记录"""
    try:
        data = request.get_json()
        logger.info(f"收到更新成绩请求: ID={grade_id}, 数据={data}")

        # 查找成绩
        grade_index = -1
        for i, grade in enumerate(grades):
            if grade.get('id') == grade_id:
                grade_index = i
                break

        if grade_index == -1:
            return jsonify({
                'success': False,
                'message': '成绩记录不存在'
            }), 404

        grade = grades[grade_index]

        # 检查是否锁定
        if grade.get('is_locked', False):
            return jsonify({
                'success': False,
                'message': '成绩已锁定，无法修改'
            }), 400

        # 更新字段
        if 'score' in data:
            score = float(data['score'])
            max_score = float(data.get('max_score', grade.get('max_score', 100)))
            if score < 0 or score > max_score:
                return jsonify({
                    'success': False,
                    'message': f'分数必须在0-{max_score}之间'
                }), 400
            grade['score'] = score
            grade['percentage'] = (score / max_score) * 100
            grade['letter_grade'] = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
            grade['grade_point'] = 4.0 if score >= 90 else 3.0 if score >= 80 else 2.0 if score >= 70 else 1.0 if score >= 60 else 0.0

        if 'max_score' in data:
            grade['max_score'] = float(data['max_score'])

        if 'weight' in data:
            grade['weight'] = float(data['weight'])

        if 'comments' in data:
            grade['comments'] = data['comments']

        if 'improvement_suggestions' in data:
            grade['improvement_suggestions'] = data['improvement_suggestions']

        if 'is_published' in data:
            grade['is_published'] = data['is_published']
            if data['is_published'] and not grade.get('published_at'):
                grade['published_at'] = datetime.now().isoformat()

        grade['updated_at'] = datetime.now().isoformat()

        logger.info(f"成功更新成绩: {grade['exam_name']}")

        return jsonify({
            'success': True,
            'message': '成绩更新成功',
            'data': grade
        })

    except Exception as e:
        logger.error(f"更新成绩错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新成绩失败: {str(e)}'
        }), 500

@app.route('/api/grades/<int:grade_id>', methods=['DELETE'])
def delete_grade(grade_id):
    """删除成绩记录"""
    try:
        logger.info(f"收到删除成绩请求: ID={grade_id}")

        # 查找成绩
        grade_index = -1
        for i, grade in enumerate(grades):
            if grade.get('id') == grade_id:
                grade_index = i
                break

        if grade_index == -1:
            return jsonify({
                'success': False,
                'message': '成绩记录不存在'
            }), 404

        grade = grades[grade_index]

        # 检查是否锁定
        if grade.get('is_locked', False):
            return jsonify({
                'success': False,
                'message': '成绩已锁定，无法删除'
            }), 400

        deleted_grade = grades.pop(grade_index)
        logger.info(f"成功删除成绩: {deleted_grade['exam_name']}")

        return jsonify({
            'success': True,
            'message': '成绩删除成功',
            'data': deleted_grade
        })

    except Exception as e:
        logger.error(f"删除成绩错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除成绩失败: {str(e)}'
        }), 500

@app.route('/api/grades/<int:grade_id>/publish', methods=['POST'])
def publish_grade(grade_id):
    """发布成绩"""
    try:
        logger.info(f"收到发布成绩请求: ID={grade_id}")

        # 查找成绩
        grade = next((g for g in grades if g.get('id') == grade_id), None)
        if not grade:
            return jsonify({
                'success': False,
                'message': '成绩记录不存在'
            }), 404

        if grade.get('is_published', False):
            return jsonify({
                'success': False,
                'message': '成绩已发布'
            }), 400

        grade['is_published'] = True
        grade['published_at'] = datetime.now().isoformat()
        grade['updated_at'] = datetime.now().isoformat()

        logger.info(f"成功发布成绩: {grade['exam_name']}")

        return jsonify({
            'success': True,
            'message': '成绩发布成功'
        })

    except Exception as e:
        logger.error(f"发布成绩错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'发布成绩失败: {str(e)}'
        }), 500

@app.route('/api/grades/statistics', methods=['GET'])
def get_grade_statistics():
    """获取成绩统计信息"""
    try:
        total_grades = len(grades)
        published_grades = len([g for g in grades if g.get('is_published', False)])
        unpublished_grades = total_grades - published_grades

        # 按考试类型统计
        grades_by_type = {}
        for grade in grades:
            exam_type = grade.get('exam_type', 'unknown')
            grades_by_type[exam_type] = grades_by_type.get(exam_type, 0) + 1

        # 按学期统计
        grades_by_semester = {}
        for grade in grades:
            semester = grade.get('semester', 'unknown')
            grades_by_semester[semester] = grades_by_semester.get(semester, 0) + 1

        # 平均分统计
        avg_scores = {}
        exam_types = set(g.get('exam_type') for g in grades if g.get('exam_type'))
        for exam_type in exam_types:
            type_scores = [g.get('score') for g in grades if g.get('exam_type') == exam_type and g.get('score') is not None]
            if type_scores:
                avg_scores[exam_type] = sum(type_scores) / len(type_scores)

        # 及格率统计
        pass_rates = {}
        for exam_type in exam_types:
            type_grades = [g for g in grades if g.get('exam_type') == exam_type]
            if type_grades:
                passed = len([g for g in type_grades if g.get('score', 0) >= 60])
                pass_rates[exam_type] = (passed / len(type_grades)) * 100

        # 成绩分布
        score_distribution = {
            '90-100': len([g for g in grades if g.get('score', 0) >= 90]),
            '80-89': len([g for g in grades if 80 <= g.get('score', 0) < 90]),
            '70-79': len([g for g in grades if 70 <= g.get('score', 0) < 80]),
            '60-69': len([g for g in grades if 60 <= g.get('score', 0) < 70]),
            '0-59': len([g for g in grades if g.get('score', 0) < 60])
        }

        statistics = {
            'total_grades': total_grades,
            'published_grades': published_grades,
            'unpublished_grades': unpublished_grades,
            'grades_by_type': grades_by_type,
            'grades_by_semester': grades_by_semester,
            'average_scores': avg_scores,
            'pass_rates': pass_rates,
            'score_distribution': score_distribution
        }

        return jsonify({
            'success': True,
            'data': statistics
        })

    except Exception as e:
        logger.error(f"获取成绩统计错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取成绩统计失败: {str(e)}'
        }), 500

# 个人信息增强路由
@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """获取当前用户的完整个人信息"""
    try:
        # 模拟获取当前用户ID（实际应该从token中获取）
        current_user_id = request.args.get('user_id', 1, type=int)
        viewer_role = request.args.get('viewer_role', 'self')  # self/teacher/admin

        # 查找用户信息
        user = next((u for u in users if u.get('id') == current_user_id), None)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 模拟构建完整的个人信息
        profile = {
            'id': user['id'],
            'username': user['username'],
            'real_name': user.get('real_name', ''),
            'email': user.get('email', ''),
            'phone': '13800138000',  # 示例手机号
            'gender': '男',
            'birthday': '2000-01-01',
            'address': '北京市海淀区中关村大街1号',
            'city': '北京市',
            'province': '北京',
            'postal_code': '100000',
            'department': '计算机学院',
            'major': '计算机科学与技术',
            'degree': '本科',
            'student_id': 'S2021001',
            'employee_id': 'T001',
            'join_date': '2021-09-01',
            'role': user['role'],
            'status': user.get('status', 'active'),
            'avatar_url': user.get('avatar_url', ''),
            'created_at': user.get('created_at', ''),
            'last_login': datetime.now().isoformat()
        }

        # 应用隐私过滤
        if PrivacyFilter:
            profile = PrivacyFilter.filter_user_data(
                profile,
                viewer_role=viewer_role,
                include_sensitive=(viewer_role == 'self' or viewer_role == 'admin')
            )

        # 记录访问日志
        if PrivacyFilter:
            PrivacyFilter.AuditLogger.log_data_access(
                user_id=1,  # 访问者ID
                target_id=current_user_id,
                action='view',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                accessed_fields=list(profile.keys())
            )

        return jsonify({
            'success': True,
            'data': profile
        })

    except Exception as e:
        logger.error(f"获取个人信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取个人信息失败'
        }), 500

@app.route('/api/auth/profile', methods=['PUT'])
def update_profile():
    """更新个人信息"""
    try:
        data = request.get_json()
        current_user_id = data.get('id', 1)

        # 查找用户
        user_index = -1
        for i, u in enumerate(users):
            if u.get('id') == current_user_id:
                user_index = i
                break

        if user_index == -1:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 记录变更前的数据
        old_data = users[user_index].copy()

        # 更新用户基本信息
        if 'real_name' in data:
            users[user_index]['real_name'] = data['real_name']
        if 'email' in data:
            users[user_index]['email'] = data['email']
        if 'phone' in data:
            users[user_index]['phone'] = data['phone']

        # 添加变更历史记录
        change_record = {
            'id': len(profile_history) + 1,
            'user_id': current_user_id,
            'timestamp': datetime.now().isoformat(),
            'changes': [],
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }

        # 记录具体变更
        for key, value in data.items():
            if key in old_data and old_data[key] != value:
                change_record['changes'].append({
                    'field': key,
                    'old_value': old_data[key],
                    'new_value': value
                })

        if change_record['changes']:
            profile_history.append(change_record)

        # 记录审计日志
        if PrivacyFilter:
            PrivacyFilter.AuditLogger.log_data_access(
                user_id=current_user_id,
                target_id=current_user_id,
                action='update',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                accessed_fields=list(data.keys())
            )

        return jsonify({
            'success': True,
            'message': '个人信息更新成功',
            'data': users[user_index]
        })

    except Exception as e:
        logger.error(f"更新个人信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新个人信息失败'
        }), 500

@app.route('/api/auth/avatar', methods=['POST'])
def upload_avatar():
    """上传头像"""
    try:
        # 支持Base64和文件上传两种方式
        if 'avatar' in request.form:
            # Base64方式
            import base64
            avatar_data = request.form['avatar']
            # 移除data:image/...;base64,前缀
            if avatar_data.startswith('data:image'):
                avatar_data = avatar_data.split(',')[1]
            file_data = base64.b64decode(avatar_data)
            filename = f"avatar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            current_user_id = request.form.get('user_id', 1, type=int)

            if file_handler:
                result = file_handler.save_avatar(file_data, filename, current_user_id)
            else:
                # 模拟返回
                result = {
                    'file_url': '/api/files/avatars/default.jpg',
                    'filename': filename,
                    'file_size': len(file_data)
                }
        elif 'avatar' in request.files:
            # 文件上传方式
            if not file_handler:
                return jsonify({
                    'success': False,
                    'message': '文件上传功能不可用'
                }), 500

            file = request.files['avatar']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': '没有选择文件'
                }), 400

            # 读取文件数据
            file_data = file.read()
            file.seek(0)

            # 保存文件
            current_user_id = request.form.get('user_id', 1, type=int)
            result = file_handler.save_avatar(file_data, file.filename, current_user_id)
        else:
            return jsonify({
                'success': False,
                'message': '请提供头像数据'
            }), 400

        # 更新用户头像URL
        user_index = -1
        for i, u in enumerate(users):
            if u.get('id') == current_user_id:
                user_index = i
                users[user_index]['avatar_url'] = result['file_url']
                break

        # 记录审计日志
        if PrivacyFilter:
            PrivacyFilter.AuditLogger.log_data_access(
                user_id=current_user_id,
                target_id=current_user_id,
                action='update',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                accessed_fields=['avatar_url']
            )

        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'data': result
        })

    except Exception as e:
        logger.error(f"上传头像错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'上传头像失败: {str(e)}'
        }), 500

@app.route('/api/files/avatars/<filename>', methods=['GET'])
def get_avatar(filename):
    """获取头像文件"""
    try:
        avatar_path = os.path.join(file_handler.upload_folder, 'avatars', filename) if file_handler else None
        if not avatar_path or not os.path.exists(avatar_path):
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404

        return send_file(avatar_path)

    except Exception as e:
        logger.error(f"获取头像错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取文件失败'
        }), 500

@app.route('/api/auth/profile/history', methods=['GET'])
def get_profile_history():
    """获取个人信息变更历史"""
    try:
        current_user_id = request.args.get('user_id', 1, type=int)

        # 获取用户的变更历史
        user_history = [h for h in profile_history if h.get('user_id') == current_user_id]
        user_history.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            'success': True,
            'data': user_history
        })

    except Exception as e:
        logger.error(f"获取变更历史错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取变更历史失败'
        }), 500

@app.route('/api/auth/profile/export', methods=['GET'])
def export_profile():
    """导出个人信息"""
    try:
        current_user_id = request.args.get('user_id', 1, type=int)
        export_format = request.args.get('format', 'json')

        # 获取个人信息
        user = next((u for u in users if u.get('id') == current_user_id), None)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        profile = {
            '个人信息': {
                '姓名': user.get('real_name', ''),
                '用户名': user['username'],
                '邮箱': user.get('email', ''),
                '手机': '13800138000',
                '性别': '男',
                '生日': '2000-01-01'
            },
            '教育信息': {
                '部门': '计算机学院',
                '专业': '计算机科学与技术',
                '学位': '本科',
                '学号': 'S2021001'
            },
            '地址信息': {
                '地址': '北京市海淀区中关村大街1号',
                '城市': '北京市',
                '省份': '北京',
                '邮编': '100000'
            },
            '系统信息': {
                '角色': user['role'],
                '状态': user.get('status', 'active'),
                '注册时间': user.get('created_at', ''),
                '最后登录': datetime.now().isoformat()
            }
        }

        if export_format == 'json':
            return jsonify({
                'success': True,
                'data': profile
            })
        else:
            # 这里可以添加其他格式的导出，如PDF、CSV等
            return jsonify({
                'success': False,
                'message': f'不支持的导出格式: {export_format}'
            }), 400

    except Exception as e:
        logger.error(f"导出个人信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '导出失败'
        }), 500

@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        current_user_id = data.get('user_id', 1)

        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # 验证必填字段
        if not all([old_password, new_password, confirm_password]):
            return jsonify({
                'success': False,
                'message': '请填写完整的密码信息'
            }), 400

        # 验证新密码确认
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': '两次输入的新密码不一致'
            }), 400

        # 验证新密码强度
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': '新密码长度不能少于8位'
            }), 400

        # 查找用户
        user_index = -1
        for i, u in enumerate(users):
            if u.get('id') == current_user_id:
                user_index = i
                break

        if user_index == -1:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 验证旧密码（实际应该使用加密验证）
        if users[user_index].get('password') != old_password:
            return jsonify({
                'success': False,
                'message': '原密码不正确'
            }), 400

        # 更新密码（实际应该加密存储）
        users[user_index]['password'] = new_password
        users[user_index]['updated_at'] = datetime.now().isoformat()

        # 记录密码变更历史
        change_record = {
            'id': len(profile_history) + 1,
            'user_id': current_user_id,
            'timestamp': datetime.now().isoformat(),
            'changes': [{
                'field': 'password',
                'old_value': '******',
                'new_value': '******'
            }],
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        profile_history.append(change_record)

        # 记录审计日志
        if PrivacyFilter:
            PrivacyFilter.AuditLogger.log_data_access(
                user_id=current_user_id,
                target_id=current_user_id,
                action='update',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                accessed_fields=['password']
            )

        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })

    except Exception as e:
        logger.error(f"修改密码错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '修改密码失败'
        }), 500

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

@app.route('/api/auth/permissions', methods=['GET'])
def get_user_permissions():
    """获取当前用户的权限列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'message': '缺少认证信息'
            }), 401

        # 模拟从token中解析用户信息
        token = auth_header.replace('Bearer ', '')
        if 'admin' in token.lower():
            user_role = 'admin'
        elif 'teacher' in token.lower():
            user_role = 'teacher'
        else:
            user_role = 'student'

        permissions = get_role_permissions(user_role)

        return jsonify({
            'success': True,
            'data': {
                'role': user_role,
                'permissions': permissions,
                'hierarchy_level': ROLE_HIERARCHY.get(user_role, 0)
            }
        })

    except Exception as e:
        logger.error(f"获取权限信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取权限信息失败'
        }), 500

@app.route('/api/auth/check-permission', methods=['POST'])
def check_user_permission():
    """检查用户是否具有特定权限"""
    try:
        data = request.get_json()
        required_permission = data.get('permission')

        if not required_permission:
            return jsonify({
                'success': False,
                'message': '缺少权限参数'
            }), 400

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'message': '缺少认证信息'
            }), 401

        # 模拟从token中解析用户信息
        token = auth_header.replace('Bearer ', '')
        if 'admin' in token.lower():
            user_role = 'admin'
        elif 'teacher' in token.lower():
            user_role = 'teacher'
        else:
            user_role = 'student'

        has_permission = check_permission(user_role, required_permission)

        return jsonify({
            'success': True,
            'data': {
                'has_permission': has_permission,
                'user_role': user_role,
                'required_permission': required_permission,
                'user_permissions': get_role_permissions(user_role)
            }
        })

    except Exception as e:
        logger.error(f"权限检查错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '权限检查失败'
        }), 500

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

# 用户个人数据路由
@app.route('/api/user/profile', methods=['GET', 'OPTIONS'])
def get_user_profile():
    """获取当前用户的个人信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # 在实际应用中，这里应该从JWT token中获取用户ID
        # 这里简化处理，从请求参数中获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        # 查找用户基本信息
        user = None
        for u in users:
            if str(u['id']) == user_id:
                user = u
                break

        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 根据角色返回不同的个人信息
        role = user.get('role', 'student')
        profile_data = {}

        if role == 'student':
            # 查找学生详细信息
            for student in students:
                if student['id'] == user['id']:
                    profile_data = {
                        'user_id': student['id'],
                        'student_id': student['student_id'],
                        'name': student['name'],
                        'gender': student['gender'],
                        'birth_date': student['birth_date'],
                        'phone': student['phone'],
                        'email': student['email'],
                        'major': student['major'],
                        'class_name': student['class_name'],
                        'enrollment_date': student['enrollment_date'],
                        'address': student['address'],
                        'status': student['status']
                    }
                    break
        elif role == 'teacher':
            # 查找教师详细信息
            for teacher in teachers:
                if teacher['id'] == user['id']:
                    profile_data = {
                        'user_id': teacher['id'],
                        'teacher_id': teacher['teacher_id'],
                        'name': teacher['name'],
                        'gender': teacher['gender'],
                        'birth_date': teacher['birth_date'],
                        'phone': teacher['phone'],
                        'email': teacher['email'],
                        'department': teacher['department'],
                        'title': teacher['title'],
                        'hire_date': teacher['hire_date'],
                        'address': teacher['address'],
                        'status': teacher['status']
                    }
                    break
        else:
            # 管理员信息
            profile_data = {
                'user_id': user['id'],
                'name': user['real_name'],
                'email': user['email'],
                'role': user['role'],
                'status': user.get('status', 'active')
            }

        return jsonify({
            'success': True,
            'data': profile_data
        })

    except Exception as e:
        logger.error(f"获取用户信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取用户信息失败'
        }), 500

@app.route('/api/user/courses', methods=['GET', 'OPTIONS'])
def get_user_courses():
    """获取当前用户的课程信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        # 查找用户
        user = None
        for u in users:
            if str(u['id']) == user_id:
                user = u
                break

        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        role = user.get('role', 'student')
        user_courses = []

        if role == 'student':
            # 学生只能看到自己选择的课程
            user_id_int = int(user_id)
            student_courses = [
                {
                    'course_id': course['id'],
                    'course_code': course['course_code'],
                    'course_name': course['course_name'],
                    'credits': course['credits'],
                    'teacher_name': course['teacher_name'],
                    'schedule': course['schedule'],
                    'location': course['location'],
                    'status': 'selected',
                    'enrollment_date': '2024-09-01'
                }
                for course in courses
                if user_id_int in [1, 2, 3]  # 简化：前三个学生选择了这些课程
            ]
            user_courses = student_courses

        elif role == 'teacher':
            # 教师可以看到自己教授的课程
            teacher_id_map = {1: 1, 2: 2, 3: 3, 4: 3, 5: 5, 6: 6}
            teacher_course_id = teacher_id_map.get(int(user_id), 1)

            user_courses = [
                {
                    'course_id': course['id'],
                    'course_code': course['course_code'],
                    'course_name': course['course_name'],
                    'credits': course['credits'],
                    'hours': course['hours'],
                    'course_type': course['course_type'],
                    'max_students': course['max_students'],
                    'current_students': course['current_students'],
                    'schedule': course['schedule'],
                    'location': course['location'],
                    'status': course['status'],
                    'semester': course['semester']
                }
                for course in courses
                if course['teacher_id'] == teacher_course_id
            ]

        else:
            # 管理员可以看到所有课程
            user_courses = courses

        return jsonify({
            'success': True,
            'data': user_courses
        })

    except Exception as e:
        logger.error(f"获取用户课程错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取课程信息失败'
        }), 500

@app.route('/api/user/grades', methods=['GET', 'OPTIONS'])
def get_user_grades():
    """获取当前用户的成绩信息"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        # 查找用户
        user = None
        for u in users:
            if str(u['id']) == user_id:
                user = u
                break

        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        role = user.get('role', 'student')
        user_grades = []

        if role == 'student':
            # 学生只能看到自己的成绩
            user_id_int = int(user_id)
            student_grades = [
                {
                    'grade_id': grade['id'],
                    'course_name': grade['course_name'],
                    'exam_type': grade['exam_type'],
                    'score': grade['score'],
                    'max_score': grade['max_score'],
                    'percentage': grade['percentage'],
                    'letter_grade': grade['letter_grade'],
                    'grade_point': grade['grade_point'],
                    'semester': grade['semester'],
                    'is_published': grade['is_published'],
                    'comments': grade.get('comments', ''),
                    'graded_at': grade.get('graded_at', '')
                }
                for grade in grades
                if grade['student_id'] == f"S202100{user_id_int}"  # 匹配学生学号
            ]
            user_grades = student_grades

        elif role == 'teacher':
            # 教师可以看到自己教授的课程的学生成绩
            teacher_course_map = {1: [1], 2: [2], 3: [3]}  # 简化映射
            teacher_courses = teacher_course_map.get(int(user_id), [1])

            user_grades = [
                {
                    'grade_id': grade['id'],
                    'student_name': grade['student_name'],
                    'student_id': grade['student_id'],
                    'course_name': grade['course_name'],
                    'exam_type': grade['exam_type'],
                    'score': grade['score'],
                    'max_score': grade['max_score'],
                    'percentage': grade['percentage'],
                    'letter_grade': grade['letter_grade'],
                    'semester': grade['semester'],
                    'is_published': grade['is_published'],
                    'graded_at': grade.get('graded_at', '')
                }
                for grade in grades
                if grade['course_id'] in teacher_courses
            ]

        else:
            # 管理员可以看到所有成绩
            user_grades = grades

        return jsonify({
            'success': True,
            'data': user_grades
        })

    except Exception as e:
        logger.error(f"获取用户成绩错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取成绩信息失败'
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("学生信息管理系统 - 后端服务启动")
    print("=" * 50)
    print(f"服务地址: http://localhost:5000")
    print(f"API文档: http://localhost:5000/api/health")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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