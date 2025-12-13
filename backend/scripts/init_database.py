#!/usr/bin/env python3
# ========================================
# 学生信息管理系统 - 数据库初始化脚本
# ========================================

import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import (
    User, UserRole, Student, Teacher, Course,
    Enrollment, Grade, Message, SystemConfig,
    AuditLog, AuditAction
)

def init_database():
    """初始化数据库"""
    app = create_app('development')

    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成！")

        # 创建系统配置
        create_system_configs()

        # 创建默认管理员用户
        create_admin_user()

        # 创建测试数据
        create_test_data()

        print("数据库初始化完成！")

def create_system_configs():
    """创建系统配置"""
    print("正在创建系统配置...")

    configs = [
        # 系统基础配置
        {
            'key': 'system_name',
            'value': '学生信息管理系统',
            'description': '系统名称',
            'type': 'string',
            'category': 'system'
        },
        {
            'key': 'system_version',
            'value': '1.0.0',
            'description': '系统版本',
            'type': 'string',
            'category': 'system'
        },
        {
            'key': 'max_login_attempts',
            'value': '5',
            'description': '最大登录尝试次数',
            'type': 'number',
            'category': 'security'
        },
        {
            'key': 'session_timeout',
            'value': '3600',
            'description': '会话超时时间（秒）',
            'type': 'number',
            'category': 'security'
        },
        # 学务配置
        {
            'key': 'current_semester',
            'value': '2024-春',
            'description': '当前学期',
            'type': 'string',
            'category': 'academic'
        },
        {
            'key': 'current_academic_year',
            'value': '2023-2024',
            'description': '当前学年',
            'type': 'string',
            'category': 'academic'
        },
        {
            'key': 'max_course_enrollment',
            'value': '5',
            'description': '学生最大选课数量',
            'type': 'number',
            'category': 'academic'
        },
        {
            'key': 'passing_grade',
            'value': '60',
            'description': '及格分数',
            'type': 'number',
            'category': 'academic'
        },
        # 邮件配置
        {
            'key': 'mail_enabled',
            'value': 'false',
            'description': '是否启用邮件发送',
            'type': 'boolean',
            'category': 'mail'
        },
        {
            'key': 'mail_smtp_server',
            'value': 'smtp.example.com',
            'description': 'SMTP服务器地址',
            'type': 'string',
            'category': 'mail'
        },
        {
            'key': 'mail_smtp_port',
            'value': '587',
            'description': 'SMTP服务器端口',
            'type': 'number',
            'category': 'mail'
        }
    ]

    for config_data in configs:
        existing = SystemConfig.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = SystemConfig(**config_data)
            db.session.add(config)

    db.session.commit()
    print("系统配置创建完成！")

def create_admin_user():
    """创建默认管理员用户"""
    print("正在创建默认管理员用户...")

    # 检查是否已存在管理员
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("管理员用户已存在！")
        return

    # 创建管理员用户
    admin_user = User(
        username='admin',
        email='admin@example.com',
        role=UserRole.ADMIN,
        status='active',
        email_verified=True
    )
    admin_user.password_hash = generate_password_hash('123456')

    db.session.add(admin_user)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=admin_user.id,
        action=AuditAction.CREATE,
        resource='user',
        resource_id=admin_user.id,
        details={'action': 'create_admin_user', 'username': 'admin'}
    )
    db.session.add(audit_log)

    db.session.commit()
    print("管理员用户创建成功！用户名: admin, 密码: 123456")

def create_test_data():
    """创建测试数据"""
    print("正在创建测试数据...")

    # 创建教师用户
    teachers_data = [
        {
            'username': 'teacher001',
            'email': 'zhang.wei@example.com',
            'name': '张伟',
            'gender': '男',
            'phone': '13800138001',
            'department': '计算机科学系',
            'title': '教授',
            'specialization': '人工智能'
        },
        {
            'username': 'teacher002',
            'email': 'li.ming@example.com',
            'name': '李明',
            'gender': '男',
            'phone': '13800138002',
            'department': '软件工程系',
            'title': '副教授',
            'specialization': '软件工程'
        },
        {
            'username': 'teacher003',
            'email': 'wang.fang@example.com',
            'name': '王芳',
            'gender': '女',
            'phone': '13800138003',
            'department': '计算机科学系',
            'title': '讲师',
            'specialization': '数据结构'
        }
    ]

    teachers = []
    for i, teacher_data in enumerate(teachers_data):
        # 创建用户
        user = User.query.filter_by(username=teacher_data['username']).first()
        if not user:
            user = User(
                username=teacher_data['username'],
                email=teacher_data['email'],
                role=UserRole.TEACHER,
                status='active',
                email_verified=True
            )
            user.password_hash = generate_password_hash('123456')
            db.session.add(user)
            db.session.flush()  # 获取用户ID

        # 创建教师档案
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if not teacher:
            teacher = Teacher(
                user_id=user.id,
                teacher_id=f'T{1001 + i}',
                name=teacher_data['name'],
                gender=teacher_data['gender'],
                birth_date=datetime(1980 + i, 1, 1).date(),
                phone=teacher_data['phone'],
                email=teacher_data['email'],
                address='北京市海淀区',
                department=teacher_data['department'],
                title=teacher_data['title'],
                specialization=teacher_data['specialization'],
                education='博士',
                hire_date=datetime(2010 + i, 9, 1).date()
            )
            db.session.add(teacher)
            teachers.append(teacher)

    # 创建学生用户
    students_data = [
        {
            'username': 'student001',
            'email': 'student1@example.com',
            'name': '王小明',
            'gender': '男',
            'phone': '13900139001',
            'class_id': 'CS202101',
            'class_name': '计算机科学2021级1班',
            'major': '计算机科学与技术'
        },
        {
            'username': 'student002',
            'email': 'student2@example.com',
            'name': '李小红',
            'gender': '女',
            'phone': '13900139002',
            'class_id': 'CS202101',
            'class_name': '计算机科学2021级1班',
            'major': '计算机科学与技术'
        },
        {
            'username': 'student003',
            'email': 'student3@example.com',
            'name': '张小军',
            'gender': '男',
            'phone': '13900139003',
            'class_id': 'SE202101',
            'class_name': '软件工程2021级1班',
            'major': '软件工程'
        }
    ]

    students = []
    for i, student_data in enumerate(students_data):
        # 创建用户
        user = User.query.filter_by(username=student_data['username']).first()
        if not user:
            user = User(
                username=student_data['username'],
                email=student_data['email'],
                role=UserRole.STUDENT,
                status='active',
                email_verified=True
            )
            user.password_hash = generate_password_hash('123456')
            db.session.add(user)
            db.session.flush()  # 获取用户ID

        # 创建学生档案
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            student = Student(
                user_id=user.id,
                student_id=f'S{2021001 + i}',
                name=student_data['name'],
                gender=student_data['gender'],
                birth_date=datetime(2003, 9, 1).date(),
                phone=student_data['phone'],
                email=student_data['email'],
                address='北京市朝阳区',
                class_id=student_data['class_id'],
                class_name=student_data['class_name'],
                major=student_data['major'],
                enrollment_date=datetime(2021, 9, 1).date()
            )
            db.session.add(student)
            students.append(student)

    # 创建课程
    courses_data = [
        {
            'course_code': 'CS101',
            'name': '计算机科学导论',
            'description': '计算机科学基础课程',
            'credits': 3,
            'hours': 48,
            'teacher': teachers[0],
            'max_students': 100
        },
        {
            'course_code': 'CS201',
            'name': '数据结构与算法',
            'description': '数据结构基础课程',
            'credits': 4,
            'hours': 64,
            'teacher': teachers[2],
            'max_students': 80
        },
        {
            'course_code': 'SE101',
            'name': '软件工程导论',
            'description': '软件工程基础课程',
            'credits': 3,
            'hours': 48,
            'teacher': teachers[1],
            'max_students': 60
        }
    ]

    courses = []
    for course_data in courses_data:
        course = Course.query.filter_by(course_code=course_data['course_code']).first()
        if not course:
            course = Course(
                course_code=course_data['course_code'],
                name=course_data['name'],
                description=course_data['description'],
                credits=course_data['credits'],
                hours=course_data['hours'],
                teacher_id=course_data['teacher'].id,
                semester='2024-春',
                academic_year='2023-2024',
                max_students=course_data['max_students'],
                current_students=0,
                status='published'
            )
            db.session.add(course)
            courses.append(course)

    db.session.commit()
    print("测试数据创建完成！")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)