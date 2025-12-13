# ========================================
# 学生信息管理系统 - 课程管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import (
    Course, Teacher, User, UserProfile, CourseType, CourseStatus,
    Enrollment, Grade, AuditLog, AuditAction
)
from schemas import (
    CourseSchema, CourseCreateSchema, CourseUpdateSchema,
    CourseSearchSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, not_found_response,
    forbidden_response, validation_error_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query

# 创建命名空间
courses_ns = Namespace('courses', description='课程管理相关操作')

# 定义数据模型
course_create_model = courses_ns.model('CourseCreate', {
    'course_code': fields.String(required=True, description='课程代码'),
    'name': fields.String(required=True, description='课程名称'),
    'description': fields.String(description='课程描述'),
    'credits': fields.Float(required=True, description='学分'),
    'hours_per_week': fields.Integer(required=True, description='每周课时'),
    'course_type': fields.String(required=True, description='课程类型', enum=['required', 'elective', 'professional', 'general']),
    'category': fields.String(description='课程分类'),
    'level': fields.String(description='课程级别'),
    'semester': fields.String(required=True, description='学期'),
    'academic_year': fields.String(description='学年'),
    'max_students': fields.Integer(description='最大学生数'),
    'min_students': fields.Integer(description='最小学生数'),
    'teacher_id': fields.String(description='授课教师ID'),
    'schedule': fields.Raw(description='上课时间安排'),
    'classroom': fields.String(description='教室'),
    'campus': fields.String(description='校区'),
    'prerequisites': fields.List(fields.String, description='先修课程'),
    'restrictions': fields.String(description='选课限制'),
    'materials': fields.Raw(description='课程材料'),
    'syllabus': fields.String(description='课程大纲'),
    'objectives': fields.String(description='课程目标'),
    'outcomes': fields.String(description='学习成果')
})

course_update_model = courses_ns.model('CourseUpdate', {
    'name': fields.String(description='课程名称'),
    'description': fields.String(description='课程描述'),
    'credits': fields.Float(description='学分'),
    'hours_per_week': fields.Integer(description='每周课时'),
    'course_type': fields.String(description='课程类型', enum=['required', 'elective', 'professional', 'general']),
    'category': fields.String(description='课程分类'),
    'level': fields.String(description='课程级别'),
    'semester': fields.String(description='学期'),
    'academic_year': fields.String(description='学年'),
    'max_students': fields.Integer(description='最大学生数'),
    'min_students': fields.Integer(description='最小学生数'),
    'teacher_id': fields.String(description='授课教师ID'),
    'schedule': fields.Raw(description='上课时间安排'),
    'classroom': fields.String(description='教室'),
    'campus': fields.String(description='校区'),
    'prerequisites': fields.List(fields.String, description='先修课程'),
    'restrictions': fields.String(description='选课限制'),
    'materials': fields.Raw(description='课程材料'),
    'syllabus': fields.String(description='课程大纲'),
    'objectives': fields.String(description='课程目标'),
    'outcomes': fields.String(description='学习成果'),
    'status': fields.String(description='课程状态', enum=['active', 'inactive', 'completed', 'cancelled', 'planning'])
})

course_search_model = courses_ns.model('CourseSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'course_code': fields.String(description='课程代码'),
    'teacher_id': fields.String(description='教师ID'),
    'course_type': fields.String(description='课程类型'),
    'category': fields.String(description='课程分类'),
    'semester': fields.String(description='学期'),
    'status': fields.String(description='课程状态'),
    'credits_min': fields.Float(description='学分最小值'),
    'credits_max': fields.Float(description='学分最大值'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='course_code'),
    'sort_order': fields.String(description='排序方式', default='asc')
})

@courses_ns.route('')
class CourseListResource(Resource):
    @jwt_required()
    @courses_ns.doc('list_courses')
    @courses_ns.expect(course_search_model)
    def get(self):
        """获取课程列表"""
        try:
            schema = CourseSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = Course.query

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.filter(
                    or_(
                        Course.course_code.like(keyword),
                        Course.name.like(keyword),
                        Course.description.like(keyword),
                        Course.category.like(keyword)
                    )
                )

            # 课程代码筛选
            if data.get('course_code'):
                query = query.filter(Course.course_code.like(f"%{data['course_code']}%"))

            # 教师筛选
            if data.get('teacher_id'):
                query = query.filter(Course.teacher_id == data['teacher_id'])

            # 课程类型筛选
            if data.get('course_type'):
                query = query.filter(Course.course_type == CourseType(data['course_type']))

            # 分类筛选
            if data.get('category'):
                query = query.filter(Course.category.like(f"%{data['category']}%"))

            # 学期筛选
            if data.get('semester'):
                query = query.filter(Course.semester.like(f"%{data['semester']}%"))

            # 状态筛选
            if data.get('status'):
                query = query.filter(Course.status == CourseStatus(data['status']))

            # 学分范围筛选
            if data.get('credits_min') is not None:
                query = query.filter(Course.credits >= data['credits_min'])
            if data.get('credits_max') is not None:
                query = query.filter(Course.credits <= data['credits_max'])

            # 排序
            sort_field_map = {
                'course_code': Course.course_code,
                'name': Course.name,
                'credits': Course.credits,
                'semester': Course.semester,
                'created_at': Course.created_at,
                'current_students': Course.current_students
            }

            sort_field = sort_field_map.get(data['sort_by'], Course.course_code)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            courses = pagination.items

            # 序列化
            course_schema = CourseSchema(many=True)
            course_data = course_schema.dump(courses)

            response_data = {
                'courses': course_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取课程列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @courses_ns.expect(course_create_model)
    @courses_ns.doc('create_course')
    @require_permission('course_management')
    @rate_limit("10/minute")
    def post(self):
        """创建课程"""
        try:
            schema = CourseCreateSchema()
            data = schema.load(request.json)

            # 检查课程代码唯一性
            existing_course = Course.query.filter_by(
                course_code=data['course_code'],
                semester=data['semester']
            ).first()
            if existing_course:
                return error_response("该学期课程代码已存在", 400)

            # 验证教师
            teacher = None
            if data.get('teacher_id'):
                teacher = Teacher.query.filter_by(id=data['teacher_id']).first()
                if not teacher:
                    return error_response("指定的教师不存在", 400)

            # 创建课程
            course = Course(
                course_code=data['course_code'],
                name=data['name'],
                description=data.get('description'),
                credits=data['credits'],
                hours_per_week=data['hours_per_week'],
                course_type=CourseType(data['course_type']),
                category=data.get('category'),
                level=data.get('level'),
                semester=data['semester'],
                academic_year=data.get('academic_year'),
                max_students=data.get('max_students', 50),
                min_students=data.get('min_students', 5),
                teacher_id=data.get('teacher_id'),
                schedule=data.get('schedule'),
                classroom=data.get('classroom'),
                campus=data.get('campus'),
                prerequisites=data.get('prerequisites'),
                restrictions=data.get('restrictions'),
                materials=data.get('materials'),
                syllabus=data.get('syllabus'),
                objectives=data.get('objectives'),
                outcomes=data.get('outcomes'),
                status=CourseStatus('planning')
            )
            course.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=g.current_user.id,
                resource_type='course',
                resource_id=course.id,
                resource_name=f"{data['course_code']} - {data['name']}"
            )

            # 返回课程信息
            course_schema = CourseSchema()
            course_data = course_schema.dump(course)

            return success_response("课程创建成功", course_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>')
class CourseResource(Resource):
    @jwt_required()
    @courses_ns.doc('get_course')
    def get(self, course_id):
        """获取课程详情"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 序列化
            course_schema = CourseSchema()
            course_data = course_schema.dump(course)

            return success_response("获取课程详情成功", course_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @courses_ns.expect(course_update_model)
    @courses_ns.doc('update_course')
    def put(self, course_id):
        """更新课程信息"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查权限
            if not g.current_user.has_permission('course_management'):
                return forbidden_response("权限不足")

            schema = CourseUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新课程信息
            updatable_fields = [
                'name', 'description', 'credits', 'hours_per_week', 'course_type',
                'category', 'level', 'semester', 'academic_year', 'max_students',
                'min_students', 'teacher_id', 'schedule', 'classroom', 'campus',
                'prerequisites', 'restrictions', 'materials', 'syllabus',
                'objectives', 'outcomes', 'status'
            ]

            for field in updatable_fields:
                if field in data:
                    old_value = getattr(course, field)
                    new_value = data[field]

                    # 特殊处理枚举类型
                    if field == 'course_type' and new_value:
                        new_value = CourseType(new_value)
                    elif field == 'status' and new_value:
                        new_value = CourseStatus(new_value)

                    if old_value != new_value:
                        old_values[field] = old_value.value if hasattr(old_value, 'value') else old_value
                        setattr(course, field, new_value)
                        new_values[field] = new_value.value if hasattr(new_value, 'value') else new_value

            # 验证教师
            if data.get('teacher_id') and data['teacher_id'] != course.teacher_id:
                teacher = Teacher.query.filter_by(id=data['teacher_id']).first()
                if not teacher:
                    return error_response("指定的教师不存在", 400)

            course.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='course',
                resource_id=course_id,
                resource_name=course.name,
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的课程信息
            course_schema = CourseSchema()
            course_data = course_schema.dump(course)

            return success_response("课程信息更新成功", course_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @jwt_required()
    @courses_ns.doc('delete_course')
    @require_permission('course_management')
    def delete(self, course_id):
        """删除课程"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查是否可以删除
            if course.enrollments:
                return error_response("该课程有学生选课，无法删除", 400)

            # 记录审计日志
            AuditLog.log_delete(
                user_id=g.current_user.id,
                resource_type='course',
                resource_id=course_id,
                resource_name=course.name
            )

            # 删除课程
            db.session.delete(course)
            db.session.commit()

            return success_response("课程删除成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>/activate')
class CourseActivateResource(Resource):
    @jwt_required()
    @courses_ns.doc('activate_course')
    @require_permission('course_management')
    def post(self, course_id):
        """激活课程"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            course.status = CourseStatus.ACTIVE
            course.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='course',
                resource_id=course_id,
                resource_name=course.name,
                old_values={'status': course.status.value},
                new_values={'status': 'active'}
            )

            return success_response("课程激活成功")

        except Exception as e:
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>/students')
class CourseStudentsResource(Resource):
    @jwt_required()
    @courses_ns.doc('get_course_students')
    def get(self, course_id):
        """获取课程学生列表"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 获取选课学生
            enrollments = db.session.query(Enrollment, Student, User).join(Student).join(User).filter(
                Enrollment.course_id == course_id,
                Enrollment.status == 'enrolled'
            ).all()

            students_data = []
            for enrollment, student, user in enrollments:
                student_info = {
                    'enrollment_id': enrollment.id,
                    'student_id': student.id,
                    'student_number': student.student_id,
                    'name': user.profile.full_name if user.profile else user.username,
                    'grade': student.grade,
                    'class_name': student.class_name,
                    'major': student.major,
                    'enrollment_date': enrollment.enrollment_date.isoformat()
                }
                students_data.append(student_info)

            return success_response("获取课程学生列表成功", students_data)

        except Exception as e:
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>/grades')
class CourseGradesResource(Resource):
    @jwt_required()
    @courses_ns.doc('get_course_grades')
    def get(self, course_id):
        """获取课程成绩统计"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_teacher = (g.current_user.role.value == 'teacher' and
                         hasattr(g.current_user, 'teacher_record') and
                         g.current_user.teacher_record.id == course.teacher_id)

            if not (is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            # 获取成绩统计
            grades_info = {
                'total_students': len(course.enrollments),
                'class_average': course.calculate_class_average('final'),
                'grade_distribution': course.get_grade_distribution('final'),
                'pass_rate': 0
            }

            # 计算及格率
            final_grades = course.get_final_grades()
            if final_grades:
                pass_count = sum(1 for grade in final_grades if grade.is_passing)
                grades_info['pass_rate'] = (pass_count / len(final_grades)) * 100

            return success_response("获取课程成绩统计成功", grades_info)

        except Exception as e:
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>/duplicate')
class CourseDuplicateResource(Resource):
    @jwt_required()
    @courses_ns.doc('duplicate_course')
    @require_permission('course_management')
    def post(self, course_id):
        """复制课程到新学期"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            data = request.json
            new_semester = data.get('new_semester')
            new_teacher_id = data.get('new_teacher_id')

            if not new_semester:
                return error_response("请指定新学期", 400)

            # 复制课程
            new_course = course.duplicate_for_semester(new_semester, new_teacher_id)

            # 记录审计日志
            AuditLog.log_create(
                user_id=g.current_user.id,
                resource_type='course',
                resource_id=new_course.id,
                resource_name=f"{new_course.course_code} - {new_course.name} (复制)"
            )

            # 返回新课程信息
            course_schema = CourseSchema()
            course_data = course_schema.dump(new_course)

            return success_response("课程复制成功", course_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@courses_ns.route('/<string:course_id>/stats')
class CourseStatsResource(Resource):
    @jwt_required()
    @courses_ns.doc('get_course_stats')
    def get(self, course_id):
        """获取课程统计信息"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_teacher = (g.current_user.role.value == 'teacher' and
                         hasattr(g.current_user, 'teacher_record') and
                         g.current_user.teacher_record.id == course.teacher_id)

            if not (is_teacher or g.current_user.has_permission('course_management')):
                return forbidden_response("权限不足")

            # 统计信息
            stats = {
                'course_info': {
                    'course_code': course.course_code,
                    'name': course.name,
                    'credits': course.credits,
                    'course_type': course.display_type,
                    'semester': course.semester
                },
                'enrollment': {
                    'max_students': course.max_students,
                    'current_students': course.current_students,
                    'enrollment_rate': course.enrollment_rate,
                    'is_full': course.is_full,
                    'can_enroll': course.can_enroll
                },
                'teacher': {
                    'id': course.teacher_id,
                    'name': course.teacher.user.profile.full_name if course.teacher and course.teacher.user.profile else '未分配',
                    'title': course.teacher.display_title if course.teacher else '未分配',
                    'department': course.teacher.department if course.teacher else None
                }
            }

            return success_response("获取课程统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)

@courses_ns.route('/stats')
class CourseListStatsResource(Resource):
    @jwt_required()
    @courses_ns.doc('get_course_list_stats')
    @require_permission('course_management')
    def get(self):
        """获取课程统计信息"""
        try:
            stats = {}

            # 基础统计
            stats['total_courses'] = Course.query.count()
            stats['active_courses'] = Course.query.filter_by(status=CourseStatus.ACTIVE).count()
            stats['planning_courses'] = Course.query.filter_by(status=CourseStatus.PLANNING).count()
            stats['completed_courses'] = Course.query.filter_by(status=CourseStatus.COMPLETED).count()

            # 按类型统计
            stats['courses_by_type'] = db.session.query(
                Course.course_type, db.func.count(Course.id)
            ).group_by(Course.course_type).all()
            stats['courses_by_type'] = {
                course_type.value: count for course_type, count in stats['courses_by_type']
            }

            # 按学期统计
            stats['courses_by_semester'] = db.session.query(
                Course.semester, db.func.count(Course.id)
            ).group_by(Course.semester).all()
            stats['courses_by_semester'] = dict(stats['courses_by_semester'])

            # 学分分布
            credit_ranges = [
                ('1-2学分', Course.credits <= 2),
                ('3-4学分', Course.credits > 2, Course.credits <= 4),
                ('5-6学分', Course.credits > 4, Course.credits <= 6),
                ('7+学分', Course.credits > 6)
            ]

            stats['credit_distribution'] = {}
            for label, condition in credit_ranges:
                if len(condition) == 2:
                    count = Course.query.filter(condition[0], condition[1]).count()
                else:
                    count = Course.query.filter(condition).count()
                stats['credit_distribution'][label] = count

            # 选课最多的课程
            top_enrolled = db.session.query(
                Course.course_code, Course.name, Course.current_students
            ).filter_by(status=CourseStatus.ACTIVE).order_by(
                Course.current_students.desc()
            ).limit(10).all()

            stats['top_enrolled_courses'] = [
                {
                    'course_code': code,
                    'name': name,
                    'students': students
                }
                for code, name, students in top_enrolled
            ]

            return success_response("获取课程统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)

@courses_ns.route('/search/advanced')
class CourseAdvancedSearchResource(Resource):
    @jwt_required()
    @courses_ns.doc('advanced_course_search')
    def post(self):
        """高级课程搜索"""
        try:
            data = request.json

            # 构建复杂查询
            query = Course.query

            # 多条件搜索
            if data.get('course_codes'):
                query = query.filter(Course.course_code.in_(data['course_codes']))

            if data.get('teacher_ids'):
                query = query.filter(Course.teacher_id.in_(data['teacher_ids']))

            if data.get('course_types'):
                query = query.filter(Course.course_type.in_([CourseType(t) for t in data['course_types']]))

            if data.get('semesters'):
                query = query.filter(Course.semester.in_(data['semesters']))

            if data.get('credits_range'):
                min_credits, max_credits = data['credits_range']
                query = query.filter(Course.credits.between(min_credits, max_credits))

            if data.get('student_count_range'):
                min_students, max_students = data['student_count_range']
                query = query.filter(Course.current_students.between(min_students, max_students))

            # 执行查询
            courses = query.order_by(Course.created_at.desc()).limit(data.get('limit', 50)).all()

            # 序列化
            course_schema = CourseSchema(many=True)
            course_data = course_schema.dump(courses)

            return success_response("高级搜索完成", {
                'courses': course_data,
                'total': len(course_data)
            })

        except Exception as e:
            return error_response(str(e), 500)