#!/usr/bin/env python3
# ========================================
# 学生信息管理系统 - 种子数据脚本
# ========================================

import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import (
    User, UserRole, Student, Teacher, Course,
    Enrollment, Grade, Message, SystemConfig
)

# 初始化Faker
fake = Faker('zh_CN')

def create_seed_data():
    """创建种子数据"""
    app = create_app('development')

    with app.app_context():
        print("正在创建种子数据...")

        # 创建更多教师
        create_teachers(20)

        # 创建更多学生
        create_students(100)

        # 创建更多课程
        create_courses(30)

        # 创建选课记录
        create_enrollments()

        # 创建成绩记录
        create_grades()

        # 创建消息
        create_messages()

        print("种子数据创建完成！")

def create_teachers(count=20):
    """创建教师数据"""
    print(f"正在创建 {count} 个教师...")

    departments = ['计算机科学系', '软件工程系', '信息管理系', '数学系', '物理系']
    titles = ['教授', '副教授', '讲师', '助教']
    specializations = [
        '人工智能', '机器学习', '数据挖掘', '软件工程', '计算机网络',
        '操作系统', '数据库', '编译原理', '算法设计', '信息安全'
    ]

    for i in range(count):
        # 生成唯一用户名
        username = f'teacher_{i+4:03d}'

        # 检查是否已存在
        if User.query.filter_by(username=username).first():
            continue

        # 创建用户
        user = User(
            username=username,
            email=f'teacher{i+4}@example.com',
            role=UserRole.TEACHER,
            status='active',
            email_verified=True
        )
        user.password_hash = 'pbkdf2:sha256:260000$'  # 简化的密码hash

        db.session.add(user)
        db.session.flush()

        # 创建教师档案
        teacher = Teacher(
            user_id=user.id,
            teacher_id=f'T{1004 + i}',
            name=fake.name(),
            gender=random.choice(['男', '女']),
            birth_date=fake.date_of_birth(minimum_age=30, maximum_age=65),
            phone=fake.phone_number(),
            email=user.email,
            address=fake.address(),
            department=random.choice(departments),
            title=random.choice(titles),
            specialization=random.choice(specializations),
            education=random.choice(['学士', '硕士', '博士']),
            hire_date=fake.date_between(start_date='-10y', end_date='today')
        )
        db.session.add(teacher)

    db.session.commit()
    print(f"教师创建完成！")

def create_students(count=100):
    """创建学生数据"""
    print(f"正在创建 {count} 个学生...")

    classes = [
        ('CS202101', '计算机科学2021级1班', '计算机科学与技术'),
        ('CS202102', '计算机科学2021级2班', '计算机科学与技术'),
        ('SE202101', '软件工程2021级1班', '软件工程'),
        ('SE202102', '软件工程2021级2班', '软件工程'),
        ('IM202101', '信息管理2021级1班', '信息管理与信息系统'),
        ('MA202101', '数学2021级1班', '数学与应用数学')
    ]

    for i in range(count):
        # 生成唯一用户名
        username = f'student_{i+4:03d}'

        # 检查是否已存在
        if User.query.filter_by(username=username).first():
            continue

        # 选择班级
        class_info = random.choice(classes)

        # 创建用户
        user = User(
            username=username,
            email=f'student{i+4}@example.com',
            role=UserRole.STUDENT,
            status='active',
            email_verified=True
        )
        user.password_hash = 'pbkdf2:sha256:260000$'  # 简化的密码hash

        db.session.add(user)
        db.session.flush()

        # 创建学生档案
        student = Student(
            user_id=user.id,
            student_id=f'S{2021004 + i}',
            name=fake.name(),
            gender=random.choice(['男', '女']),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=25),
            phone=fake.phone_number(),
            email=user.email,
            address=fake.address(),
            class_id=class_info[0],
            class_name=class_info[1],
            major=class_info[2],
            enrollment_date=fake.date_between(start_date='-3y', end_date='-2y')
        )
        db.session.add(student)

    db.session.commit()
    print(f"学生创建完成！")

def create_courses(count=30):
    """创建课程数据"""
    print(f"正在创建 {count} 个课程...")

    # 获取所有教师
    teachers = Teacher.query.all()
    if not teachers:
        print("没有找到教师，请先创建教师数据")
        return

    semesters = ['2023-秋', '2024-春', '2024-夏']
    course_types = [
        ('计算机科学导论', '计算机科学基础课程', 3, 48),
        ('数据结构与算法', '数据结构基础课程', 4, 64),
        ('操作系统原理', '操作系统理论课程', 4, 64),
        ('计算机网络', '网络基础课程', 3, 48),
        ('数据库系统', '数据库原理与应用', 3, 48),
        ('软件工程', '软件开发方法学', 3, 48),
        ('人工智能导论', 'AI基础课程', 3, 48),
        ('机器学习', '机器学习算法与应用', 4, 64),
        ('Web开发技术', '前后端开发技术', 3, 48),
        ('移动应用开发', '手机应用开发', 3, 48),
        ('信息安全', '信息安全基础', 3, 48),
        ('算法设计与分析', '高级算法课程', 4, 64),
        ('编译原理', '编译器设计与实现', 4, 64),
        ('计算机组成原理', '计算机体系结构', 4, 64),
        ('离散数学', '数学基础课程', 4, 64)
    ]

    for i in range(count):
        # 生成课程代码
        subject_code = random.choice(['CS', 'SE', 'IM', 'MA'])
        course_number = f'{100 + i:03d}'
        course_code = f'{subject_code}{course_number}'

        # 检查是否已存在
        if Course.query.filter_by(course_code=course_code).first():
            continue

        # 选择课程类型
        course_info = random.choice(course_types)

        course = Course(
            course_code=course_code,
            name=f"{course_info[0]} ({i+1})",
            description=course_info[1],
            credits=course_info[2],
            hours=course_info[3],
            teacher_id=random.choice(teachers).id,
            semester=random.choice(semesters),
            academic_year='2023-2024',
            max_students=random.randint(30, 120),
            current_students=0,
            status='published'
        )
        db.session.add(course)

    db.session.commit()
    print(f"课程创建完成！")

def create_enrollments():
    """创建选课记录"""
    print("正在创建选课记录...")

    # 获取所有学生和课程
    students = Student.query.limit(50).all()  # 限制部分学生创建选课记录
    courses = Course.query.filter_by(status='published').all()

    if not students or not courses:
        print("没有找到学生或课程数据")
        return

    # 为每个学生随机选择2-5门课程
    for student in students:
        # 随机选择课程
        selected_courses = random.sample(
            courses,
            k=min(random.randint(2, 5), len(courses))
        )

        for course in selected_courses:
            # 检查是否已存在选课记录
            existing = Enrollment.query.filter_by(
                student_id=student.id,
                course_id=course.id
            ).first()

            if not existing:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    semester=course.semester,
                    academic_year=course.academic_year,
                    status=random.choice(['approved', 'pending']),
                    enrollment_date=fake.date_between(
                        start_date='-6M',
                        end_date='today'
                    )
                )
                db.session.add(enrollment)

    db.session.commit()
    print("选课记录创建完成！")

def create_grades():
    """创建成绩记录"""
    print("正在创建成绩记录...")

    # 获取所有已批准的选课记录
    enrollments = Enrollment.query.filter_by(status='approved').limit(100).all()

    if not enrollments:
        print("没有找到已批准的选课记录")
        return

    grade_types = ['exam', 'assignment', 'quiz', 'project', 'final']
    grade_names = {
        'exam': '期中考试',
        'assignment': '平时作业',
        'quiz': '随堂测验',
        'project': '课程项目',
        'final': '期末考试'
    }

    for enrollment in enrollments:
        # 为每门选课创建2-4个成绩记录
        num_grades = random.randint(2, 4)
        selected_types = random.sample(grade_types, k=num_grades)

        for grade_type in selected_types:
            score = random.randint(60, 100)
            max_score = 100
            weight = 0.3 if grade_type == 'final' else 0.2

            grade = Grade(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                enrollment_id=enrollment.id,
                semester=enrollment.semester,
                academic_year=enrollment.academic_year,
                grade_type=grade_type,
                grade_name=grade_names[grade_type],
                score=score,
                max_score=max_score,
                percentage=score / max_score * 100,
                weight=weight,
                status='published',
                graded_date=fake.date_between(
                    start_date='-3M',
                    end_date='today'
                )
            )
            db.session.add(grade)

    db.session.commit()
    print("成绩记录创建完成！")

def create_messages():
    """创建消息"""
    print("正在创建消息...")

    # 获取管理员用户
    admin = User.query.filter_by(role=UserRole.ADMIN).first()
    if not admin:
        print("没有找到管理员用户")
        return

    # 系统公告
    announcements = [
        {
            'title': '系统升级通知',
            'content': '尊敬的师生们，系统将于本周六晚上进行升级维护，预计持续2小时，期间系统将无法访问。请提前做好相关安排。',
            'priority': 'high'
        },
        {
            'title': '新学期选课通知',
            'content': '新学期选课系统已开放，请同学们及时登录系统进行选课。选课时间为：2024年2月20日-2月25日。',
            'priority': 'normal'
        },
        {
            'title': '期末考试安排',
            'content': '期末考试将于2024年6月15日开始，请同学们登录系统查看具体考试时间和地点，做好考试准备。',
            'priority': 'high'
        }
    ]

    for announcement in announcements:
        message = Message(
            sender_id=admin.id,
            recipient_type='all',
            title=announcement['title'],
            content=announcement['content'],
            type='announcement',
            priority=announcement['priority'],
            status='sent',
            send_at=fake.date_time_between(start_date='-30d', end_date='today')
        )
        db.session.add(message)

    # 私人消息
    students = User.query.filter_by(role=UserRole.STUDENT).limit(10).all()
    if students:
        for student in students:
            message = Message(
                sender_id=admin.id,
                recipient_id=student.id,
                recipient_type='user',
                title='欢迎加入学生信息管理系统',
                content=f'亲爱的{student.username}，欢迎使用学生信息管理系统！如有任何问题，请随时联系管理员。',
                type='private',
                priority='normal',
                status='sent',
                send_at=fake.date_time_between(start_date='-7d', end_date='today')
            )
            db.session.add(message)

    db.session.commit()
    print("消息创建完成！")

if __name__ == '__main__':
    try:
        create_seed_data()
    except Exception as e:
        print(f"种子数据创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)