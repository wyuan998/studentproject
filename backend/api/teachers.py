# ========================================
# 学生信息管理系统 - 教师管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import (
    Teacher, User, UserProfile, TeacherTitle, TeacherStatus,
    Student, Course, Enrollment, Grade, AuditLog, AuditAction
)
from schemas import (
    TeacherSchema, TeacherCreateSchema, TeacherUpdateSchema,
    TeacherSearchSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, not_found_response,
    forbidden_response, validation_error_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query

# 创建命名空间
teachers_ns = Namespace('teachers', description='教师管理相关操作')

# 定义数据模型
teacher_create_model = teachers_ns.model('TeacherCreate', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    'confirm_password': fields.String(required=True, description='确认密码'),
    'teacher_id': fields.String(required=True, description='教师编号'),
    'title': fields.String(description='职称', enum=['lecturer', 'associate_professor', 'professor', 'assistant']),
    'department': fields.String(required=True, description='院系'),
    'first_name': fields.String(required=True, description='姓'),
    'last_name': fields.String(required=True, description='名'),
    'phone': fields.String(description='手机号码'),
    'gender': fields.String(description='性别', enum=['male', 'female', 'other']),
    'office': fields.String(description='办公室'),
    'office_phone': fields.String(description='办公电话'),
    'office_hours': fields.String(description='办公时间'),
    'specialization': fields.String(description='专业领域'),
    'research_interests': fields.String(description='研究兴趣'),
    'education_background': fields.String(description='教育背景'),
    'hire_date': fields.Date(description='入职日期'),
    'bio': fields.String(description='个人简介')
})

teacher_update_model = teachers_ns.model('TeacherUpdate', {
    'title': fields.String(description='职称', enum=['lecturer', 'associate_professor', 'professor', 'assistant']),
    'department': fields.String(description='院系'),
    'office': fields.String(description='办公室'),
    'office_phone': fields.String(description='办公电话'),
    'office_hours': fields.String(description='办公时间'),
    'specialization': fields.String(description='专业领域'),
    'research_interests': fields.String(description='研究兴趣'),
    'education_background': fields.String(description='教育背景'),
    'status': fields.String(description='状态', enum=['active', 'inactive', 'on_leave', 'retired']),
    'bio': fields.String(description='个人简介'),
    'publications': fields.List(fields.Raw, description='发表论文'),
    'projects': fields.List(fields.Raw, description='参与项目'),
    'awards': fields.List(fields.Raw, description='获奖情况'),
    'social_links': fields.Raw(description='社交媒体链接')
})

teacher_search_model = teachers_ns.model('TeacherSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'teacher_id': fields.String(description='教师编号'),
    'title': fields.String(description='职称'),
    'department': fields.String(description='院系'),
    'status': fields.String(description='状态'),
    'specialization': fields.String(description='专业领域'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='teacher_id'),
    'sort_order': fields.String(description='排序方式', default='asc')
})

@teachers_ns.route('')
class TeacherListResource(Resource):
    @jwt_required()
    @teachers_ns.doc('list_teachers')
    @teachers_ns.expect(teacher_search_model)
    def get(self):
        """获取教师列表"""
        try:
            schema = TeacherSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = Teacher.query

            # 关联查询
            query = query.join(User).join(UserProfile)

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.filter(
                    or_(
                        Teacher.teacher_id.like(keyword),
                        User.username.like(keyword),
                        UserProfile.first_name.like(keyword),
                        UserProfile.last_name.like(keyword),
                        UserProfile.email.like(keyword),
                        Teacher.specialization.like(keyword),
                        Teacher.research_interests.like(keyword)
                    )
                )

            # 教师编号筛选
            if data.get('teacher_id'):
                query = query.filter(Teacher.teacher_id.like(f"%{data['teacher_id']}%"))

            # 职称筛选
            if data.get('title'):
                query = query.filter(Teacher.title == TeacherTitle(data['title']))

            # 部门筛选
            if data.get('department'):
                query = query.filter(Teacher.department.like(f"%{data['department']}%"))

            # 状态筛选
            if data.get('status'):
                query = query.filter(Teacher.status == TeacherStatus(data['status']))

            # 专业领域筛选
            if data.get('specialization'):
                query = query.filter(Teacher.specialization.like(f"%{data['specialization']}%"))

            # 排序
            sort_field_map = {
                'teacher_id': Teacher.teacher_id,
                'title': Teacher.title,
                'department': Teacher.department,
                'hire_date': Teacher.hire_date,
                'name': UserProfile.first_name,
                'current_courses': Teacher.current_course_load
            }

            sort_field = sort_field_map.get(data['sort_by'], Teacher.teacher_id)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            teachers = pagination.items

            # 序列化
            teacher_schema = TeacherSchema(many=True)
            teacher_data = teacher_schema.dump(teachers)

            response_data = {
                'teachers': teacher_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取教师列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @teachers_ns.expect(teacher_create_model)
    @teachers_ns.doc('create_teacher')
    @require_permission('teacher_management')
    @rate_limit("10/minute")
    def post(self):
        """创建教师"""
        try:
            schema = TeacherCreateSchema()
            data = schema.load(request.json)

            # 检查用户名和邮箱唯一性
            if User.query.filter_by(username=data['username']).first():
                return error_response("用户名已存在", 400)

            if User.query.filter_by(email=data['email']).first():
                return error_response("邮箱已存在", 400)

            # 检查教师编号唯一性
            if Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
                return error_response("教师编号已存在", 400)

            # 创建用户
            user = User(
                username=data['username'],
                email=data['email'],
                role='teacher',
                status='active',
                email_verified=True
            )
            from utils.auth import generate_password_hash
            user.password_hash = generate_password_hash(data['password'])
            user.save()

            # 创建用户资料
            profile = UserProfile(
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                gender=data.get('gender'),
                department=data['department']
            )
            profile.save()

            # 创建教师记录
            teacher = Teacher(
                user_id=user.id,
                teacher_id=data['teacher_id'],
                title=TeacherTitle(data['title']) if data.get('title') else None,
                department=data['department'],
                office=data.get('office'),
                office_phone=data.get('office_phone'),
                office_hours=data.get('office_hours'),
                specialization=data.get('specialization'),
                research_interests=data.get('research_interests'),
                education_background=data.get('education_background'),
                hire_date=data.get('hire_date'),
                status=TeacherStatus(data.get('status', 'active')),
                bio=data.get('bio')
            )
            teacher.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=g.current_user.id,
                resource_type='teacher',
                resource_id=teacher.id,
                resource_name=f"{data['teacher_id']} - {data['first_name']} {data['last_name']}"
            )

            # 返回教师信息
            teacher_schema = TeacherSchema()
            teacher_data = teacher_schema.dump(teacher)

            return success_response("教师创建成功", teacher_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>')
class TeacherResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher')
    def get(self, teacher_id):
        """获取教师详情"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 序列化
            teacher_schema = TeacherSchema()
            teacher_data = teacher_schema.dump(teacher)

            return success_response("获取教师详情成功", teacher_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @teachers_ns.expect(teacher_update_model)
    @teachers_ns.doc('update_teacher')
    def put(self, teacher_id):
        """更新教师信息"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限：本人或管理员
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('teacher_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            schema = TeacherUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新教师基本信息
            updatable_fields = [
                'title', 'department', 'office', 'office_phone', 'office_hours',
                'specialization', 'research_interests', 'education_background',
                'status', 'bio', 'publications', 'projects', 'awards', 'social_links'
            ]

            # 只有管理员可以修改部分字段
            admin_only_fields = ['status', 'title', 'department']

            for field in updatable_fields:
                if field in data:
                    if field in admin_only_fields and not has_permission:
                        continue

                    old_value = getattr(teacher, field)
                    new_value = data[field]

                    # 特殊处理枚举类型
                    if field == 'title' and new_value:
                        new_value = TeacherTitle(new_value)
                    elif field == 'status' and new_value:
                        new_value = TeacherStatus(new_value)

                    if old_value != new_value:
                        old_values[field] = old_value.value if hasattr(old_value, 'value') else old_value
                        setattr(teacher, field, new_value)
                        new_values[field] = new_value.value if hasattr(new_value, 'value') else new_value

            # 更新用户资料（本人或管理员）
            if is_self or has_permission:
                profile_fields = ['phone', 'address', 'city', 'province']

                if teacher.user.profile:
                    for field in profile_fields:
                        if field in data:
                            old_value = getattr(teacher.user.profile, field)
                            new_value = data[field]

                            if old_value != new_value:
                                old_values[f'profile_{field}'] = old_value
                                setattr(teacher.user.profile, field, new_value)
                                new_values[f'profile_{field}'] = new_value

            teacher.save()
            if teacher.user.profile:
                teacher.user.profile.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='teacher',
                resource_id=teacher_id,
                resource_name=teacher.teacher_id,
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的教师信息
            teacher_schema = TeacherSchema()
            teacher_data = teacher_schema.dump(teacher)

            return success_response("教师信息更新成功", teacher_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @jwt_required()
    @teachers_ns.doc('delete_teacher')
    @require_permission('teacher_management')
    def delete(self, teacher_id):
        """删除教师"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查是否可以删除
            if teacher.courses:
                return error_response("该教师有授课课程，无法删除", 400)

            # 记录审计日志
            AuditLog.log_delete(
                user_id=g.current_user.id,
                resource_type='teacher',
                resource_id=teacher_id,
                resource_name=teacher.teacher_id
            )

            # 删除教师（级联删除相关数据）
            db.session.delete(teacher)
            db.session.commit()

            return success_response("教师删除成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>/courses')
class TeacherCoursesResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_courses')
    def get(self, teacher_id):
        """获取教师授课课程列表"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限：本人或管理员
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('course_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            # 获取授课课程
            courses = Course.query.filter_by(teacher_id=teacher_id).all()

            courses_data = []
            for course in courses:
                course_info = {
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'course_type': course.display_type,
                    'semester': course.semester,
                    'status': course.display_status,
                    'current_students': course.current_students,
                    'max_students': course.max_students,
                    'classroom': course.classroom,
                    'schedule': course.schedule
                }
                courses_data.append(course_info)

            return success_response("获取教师授课课程成功", {
                'teacher_info': {
                    'teacher_id': teacher.teacher_id,
                    'name': teacher.user.profile.full_name if teacher.user.profile else teacher.user.username,
                    'title': teacher.display_title,
                    'department': teacher.department
                },
                'courses': courses_data
            })

        except Exception as e:
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>/students')
class TeacherStudentsResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_students')
    def get(self, teacher_id):
        """获取教师指导学生列表"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限：本人或管理员
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('student_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            # 获取指导学生
            advisees = teacher.get_all_advisees()

            students_data = []
            for student in advisees:
                student_info = {
                    'student_id': student.id,
                    'student_number': student.student_id,
                    'name': student.user.profile.full_name if student.user.profile else student.user.username,
                    'grade': student.grade,
                    'class_name': student.class_name,
                    'major': student.major,
                    'academic_status': student.display_status,
                    'gpa': student.gpa,
                    'credits_earned': student.credits_earned,
                    'email': student.user.email
                }
                students_data.append(student_info)

            return success_response("获取教师指导学生成功", {
                'teacher_info': {
                    'teacher_id': teacher.teacher_id,
                    'name': teacher.user.profile.full_name if teacher.user.profile else teacher.user.username,
                    'title': teacher.display_title,
                    'department': teacher.department
                },
                'students': students_data
            })

        except Exception as e:
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>/advisees-by-grade')
class TeacherAdviseesByGradeResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_advisees_by_grade')
    def get(self, teacher_id):
        """按年级获取教师指导学生"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('student_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            # 按年级分组指导学生
            advisees_by_grade = {}
            grades = db.session.query(Student.grade).distinct().all()

            for grade_obj in grades:
                grade = grade_obj.grade
                students = teacher.get_advisees_by_grade(grade)

                advisees_by_grade[grade] = []
                for student in students:
                    student_info = {
                        'student_id': student.id,
                        'student_number': student.student_id,
                        'name': student.user.profile.full_name if student.user.profile else student.user.username,
                        'class_name': student.class_name,
                        'major': student.major,
                        'academic_status': student.display_status,
                        'gpa': student.gpa
                    }
                    advisees_by_grade[grade].append(student_info)

            return success_response("获取按年级分组的指导学生成功", {
                'teacher_info': {
                    'teacher_id': teacher.teacher_id,
                    'name': teacher.user.profile.full_name if teacher.user.profile else teacher.user.username
                },
                'advisees_by_grade': advisees_by_grade
            })

        except Exception as e:
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>/schedule')
class TeacherScheduleResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_schedule')
    def get(self, teacher_id):
        """获取教师课表"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('course_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            # 获取当前学期课程
            from datetime import date
            current_year = date.today().year
            current_month = date.today().month

            if current_month >= 9:
                current_semester = f"{current_year}秋季"
            elif current_month >= 2:
                current_semester = f"{current_year}春季"
            else:
                current_semester = f"{current_year-1}秋季"

            courses = Course.query.filter(
                Course.teacher_id == teacher_id,
                Course.semester == current_semester,
                Course.status == 'active'
            ).all()

            schedule = []
            for course in courses:
                # 获取选课学生数量
                student_count = Enrollment.query.filter_by(
                    course_id=course.id,
                    status='enrolled'
                ).count()

                course_info = {
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'classroom': course.classroom,
                    'schedule': course.schedule,
                    'current_students': student_count,
                    'max_students': course.max_students,
                    'office_hours': course.teacher.office_hours
                }
                schedule.append(course_info)

            return success_response("获取教师课表成功", {
                'teacher_info': {
                    'teacher_id': teacher.teacher_id,
                    'name': teacher.user.profile.full_name if teacher.user.profile else teacher.user.username,
                    'office': teacher.office,
                    'office_hours': teacher.office_hours
                },
                'semester': current_semester,
                'schedule': schedule
            })

        except Exception as e:
            return error_response(str(e), 500)

@teachers_ns.route('/<string:teacher_id>/workload')
class TeacherWorkloadResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_workload')
    def get(self, teacher_id):
        """获取教师工作量统计"""
        try:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return not_found_response("教师不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_self = teacher.user_id == current_user_id
            has_permission = g.current_user.has_permission('teacher_management')

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            # 更新当前课程负荷
            teacher.update_course_load()

            workload = {
                'teacher_info': {
                    'teacher_id': teacher.teacher_id,
                    'name': teacher.user.profile.full_name if teacher.user.profile else teacher.user.username,
                    'title': teacher.display_title
                },
                'current_workload': {
                    'max_courses_per_semester': teacher.max_courses_per_semester,
                    'current_course_load': teacher.current_course_load,
                    'can_teach_more': teacher.can_teach_more_courses,
                    'utilization_rate': round((teacher.current_course_load / teacher.max_courses_per_semester) * 100, 2)
                },
                'current_courses': teacher.current_courses,
                'total_students': teacher.total_students
            }

            return success_response("获取教师工作量统计成功", workload)

        except Exception as e:
            return error_response(str(e), 500)

@teachers_ns.route('/stats')
class TeacherStatsResource(Resource):
    @jwt_required()
    @teachers_ns.doc('get_teacher_stats')
    @require_permission('teacher_management')
    def get(self):
        """获取教师统计信息"""
        try:
            stats = {}

            # 基础统计
            stats['total_teachers'] = Teacher.query.count()
            stats['active_teachers'] = Teacher.query.filter_by(status=TeacherStatus.ACTIVE).count()
            stats['inactive_teachers'] = Teacher.query.filter_by(status=TeacherStatus.INACTIVE).count()
            stats['on_leave_teachers'] = Teacher.query.filter_by(status=TeacherStatus.ON_LEAVE).count()
            stats['retired_teachers'] = Teacher.query.filter_by(status=TeacherStatus.RETIRED).count()

            # 按职称统计
            stats['teachers_by_title'] = db.session.query(
                Teacher.title, db.func.count(Teacher.id)
            ).group_by(Teacher.title).all()
            stats['teachers_by_title'] = {
                title.value: count for title, count in stats['teachers_by_title']
            }

            # 按部门统计
            stats['teachers_by_department'] = db.session.query(
                Teacher.department, db.func.count(Teacher.id)
            ).group_by(Teacher.department).all()
            stats['teachers_by_department'] = dict(stats['teachers_by_department'])

            # 教学经验统计
            experience_ranges = [
                ('0-5年', Teacher.hire_date >= (datetime.utcnow() - timedelta(days=365 * 5))),
                ('5-10年', Teacher.hire_date >= (datetime.utcnow() - timedelta(days=365 * 10)), Teacher.hire_date < (datetime.utcnow() - timedelta(days=365 * 5))),
                ('10-15年', Teacher.hire_date >= (datetime.utcnow() - timedelta(days=365 * 15)), Teacher.hire_date < (datetime.utcnow() - timedelta(days=365 * 10))),
                ('15年以上', Teacher.hire_date < (datetime.utcnow() - timedelta(days=365 * 15)))
            ]

            stats['experience_distribution'] = {}
            for label, condition in experience_ranges:
                if len(condition) == 2:
                    count = Teacher.query.filter(condition[0], condition[1]).count()
                else:
                    count = Teacher.query.filter(condition).count()
                stats['experience_distribution'][label] = count

            # 平均课程负荷
            avg_workload = db.session.query(db.func.avg(Teacher.current_course_load)).filter(
                Teacher.status == TeacherStatus.ACTIVE
            ).scalar()
            stats['average_workload'] = round(avg_workload, 2) if avg_workload else 0

            # 新入职教师（最近一年）
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            stats['new_teachers'] = Teacher.query.filter(
                Teacher.hire_date >= one_year_ago
            ).count()

            return success_response("获取教师统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)