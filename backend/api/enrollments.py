# ========================================
# 学生信息管理系统 - 选课管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import (
    Enrollment, Student, Course, User, UserProfile,
    EnrollmentStatus, AuditLog, AuditAction
)
from schemas import (
    EnrollmentSchema, EnrollmentCreateSchema, EnrollmentUpdateSchema,
    EnrollmentSearchSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, not_found_response,
    forbidden_response, validation_error_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query

# 创建命名空间
enrollments_ns = Namespace('enrollments', description='选课管理相关操作')

# 定义数据模型
enrollment_create_model = enrollments_ns.model('EnrollmentCreate', {
    'student_id': fields.String(required=True, description='学生ID'),
    'course_id': fields.String(required=True, description='课程ID'),
    'semester': fields.String(required=True, description='学期'),
    'enrollment_type': fields.String(description='选课类型', enum=['regular', 'retake', 'audit']),
    'notes': fields.String(description='备注')
})

enrollment_update_model = enrollments_ns.model('EnrollmentUpdate', {
    'status': fields.String(description='选课状态', enum=['enrolled', 'dropped', 'completed', 'failed', 'auditing']),
    'notes': fields.String(description='备注'),
    'special_needs': fields.String(description='特殊需求')
})

enrollment_search_model = enrollments_ns.model('EnrollmentSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'student_id': fields.String(description='学生ID'),
    'course_id': fields.String(description='课程ID'),
    'semester': fields.String(description='学期'),
    'status': fields.String(description='选课状态'),
    'enrollment_type': fields.String(description='选课类型'),
    'teacher_id': fields.String(description='教师ID'),
    'start_date': fields.Date(description='开始日期'),
    'end_date': fields.Date(description='结束日期'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='enrollment_date'),
    'sort_order': fields.String(description='排序方式', default='desc')
})

bulk_enrollment_model = enrollments_ns.model('BulkEnrollment', {
    'course_id': fields.String(required=True, description='课程ID'),
    'student_ids': fields.List(fields.String, required=True, description='学生ID列表'),
    'semester': fields.String(required=True, description='学期'),
    'enrollment_type': fields.String(description='选课类型', enum=['regular', 'retake', 'audit'])
})

@enrollments_ns.route('')
class EnrollmentListResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('list_enrollments')
    @enrollments_ns.expect(enrollment_search_model)
    def get(self):
        """获取选课列表"""
        try:
            schema = EnrollmentSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = Enrollment.query

            # 关联查询
            query = query.join(Student).join(User).join(Course)

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.filter(
                    or_(
                        Student.student_id.like(keyword),
                        User.username.like(keyword),
                        UserProfile.first_name.like(keyword),
                        UserProfile.last_name.like(keyword),
                        Course.course_code.like(keyword),
                        Course.name.like(keyword)
                    )
                )

            # 学生筛选
            if data.get('student_id'):
                query = query.filter(Enrollment.student_id == data['student_id'])

            # 课程筛选
            if data.get('course_id'):
                query = query.filter(Enrollment.course_id == data['course_id'])

            # 学期筛选
            if data.get('semester'):
                query = query.filter(Enrollment.semester.like(f"%{data['semester']}%"))

            # 状态筛选
            if data.get('status'):
                query = query.filter(Enrollment.status == EnrollmentStatus(data['status']))

            # 选课类型筛选
            if data.get('enrollment_type'):
                query = query.filter(Enrollment.enrollment_type == data['enrollment_type'])

            # 教师筛选（通过课程）
            if data.get('teacher_id'):
                query = query.filter(Course.teacher_id == data['teacher_id'])

            # 日期范围筛选
            if data.get('start_date'):
                query = query.filter(Enrollment.enrollment_date >= data['start_date'])
            if data.get('end_date'):
                query = query.filter(Enrollment.enrollment_date <= data['end_date'])

            # 排序
            sort_field_map = {
                'enrollment_date': Enrollment.enrollment_date,
                'student_id': Student.student_id,
                'course_code': Course.course_code,
                'status': Enrollment.status,
                'semester': Enrollment.semester
            }

            sort_field = sort_field_map.get(data['sort_by'], Enrollment.enrollment_date)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            enrollments = pagination.items

            # 序列化
            enrollment_schema = EnrollmentSchema(many=True)
            enrollment_data = enrollment_schema.dump(enrollments)

            response_data = {
                'enrollments': enrollment_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取选课列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @enrollments_ns.expect(enrollment_create_model)
    @enrollments_ns.doc('create_enrollment')
    def post(self):
        """学生选课"""
        try:
            schema = EnrollmentCreateSchema()
            data = schema.load(request.json)

            current_user_id = get_jwt_identity()

            # 检查权限：学生只能为自己选课，管理员可以为任意学生选课
            if not g.current_user.has_permission('enrollment_management'):
                # 学生选课，检查是否为自己
                student = Student.query.filter_by(user_id=current_user_id).first()
                if not student or student.id != data['student_id']:
                    return forbidden_response("只能为自己选课")

            # 验证学生和课程
            student = Student.query.get(data['student_id'])
            if not student:
                return not_found_response("学生不存在")

            course = Course.query.get(data['course_id'])
            if not course:
                return not_found_response("课程不存在")

            # 检查选课条件
            can_enroll, message = course.can_student_enroll(student)
            if not can_enroll:
                return error_response(message, 400)

            # 检查是否已选过
            existing_enrollment = Enrollment.query.filter_by(
                student_id=data['student_id'],
                course_id=data['course_id'],
                semester=data['semester']
            ).first()

            if existing_enrollment:
                if existing_enrollment.status == EnrollmentStatus.ENROLLED:
                    return error_response("已经选过此课程", 400)
                elif existing_enrollment.status in [EnrollmentStatus.COMPLETED, EnrollmentStatus.FAILED]:
                    return error_response("此课程已完成，如需重修请选择重修类型", 400)
                elif existing_enrollment.status == EnrollmentStatus.DROPPED:
                    # 重新激活退选的课程
                    existing_enrollment.status = EnrollmentStatus.ENROLLED
                    existing_enrollment.drop_date = None
                    existing_enrollment.save()
                else:
                    existing_enrollment.status = EnrollmentStatus.ENROLLED
                    existing_enrollment.save()
            else:
                # 创建新选课记录
                enrollment = Enrollment(
                    student_id=data['student_id'],
                    course_id=data['course_id'],
                    semester=data['semester'],
                    enrollment_type=data.get('enrollment_type', 'regular'),
                    status=EnrollmentStatus.ENROLLED,
                    notes=data.get('notes')
                )
                enrollment.save()

            # 更新课程选课人数
            course.update_current_students()

            # 记录审计日志
            AuditLog.log_create(
                user_id=current_user_id,
                resource_type='enrollment',
                resource_id=enrollment.id if 'enrollment' in locals() else existing_enrollment.id,
                resource_name=f"{student.student_id} 选修 {course.course_code}"
            )

            # 返回选课信息
            enrollment_obj = enrollment if 'enrollment' in locals() else existing_enrollment
            enrollment_schema = EnrollmentSchema()
            enrollment_data = enrollment_schema.dump(enrollment_obj)

            return success_response("选课成功", enrollment_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@enrollments_ns.route('/<string:enrollment_id>')
class EnrollmentResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('get_enrollment')
    def get(self, enrollment_id):
        """获取选课详情"""
        try:
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return not_found_response("选课记录不存在")

            # 检查权限：学生本人、教师或管理员
            current_user_id = get_jwt_identity()

            # 检查是否是学生本人
            student = Student.query.filter_by(user_id=current_user_id).first()
            is_self = student and student.id == enrollment.student_id

            # 检查是否是授课教师
            is_teacher = (g.current_user.role.value == 'teacher' and
                         enrollment.course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            # 检查是否有管理权限
            has_permission = g.current_user.has_permission('enrollment_management')

            if not (is_self or is_teacher or has_permission):
                return forbidden_response("权限不足")

            # 序列化
            enrollment_schema = EnrollmentSchema()
            enrollment_data = enrollment_schema.dump(enrollment)

            return success_response("获取选课详情成功", enrollment_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @enrollments_ns.expect(enrollment_update_model)
    @enrollments_ns.doc('update_enrollment')
    def put(self, enrollment_id):
        """更新选课信息"""
        try:
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return not_found_response("选课记录不存在")

            # 检查权限
            if not g.current_user.has_permission('enrollment_management'):
                return forbidden_response("权限不足")

            schema = EnrollmentUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值
            old_values = {}
            new_values = {}

            # 更新选课信息
            if data.get('status') and data['status'] != enrollment.status.value:
                old_values['status'] = enrollment.status.value
                enrollment.status = EnrollmentStatus(data['status'])
                new_values['status'] = data['status']

                # 处理状态变更的特殊逻辑
                if data['status'] == 'dropped':
                    enrollment.drop_course()
                elif data['status'] == 'completed':
                    # 可以添加完成课程的逻辑
                    pass

            if data.get('notes'):
                old_values['notes'] = enrollment.notes
                enrollment.notes = data['notes']
                new_values['notes'] = data['notes']

            if data.get('special_needs'):
                old_values['special_needs'] = enrollment.special_needs
                enrollment.special_needs = data['special_needs']
                new_values['special_needs'] = data['special_needs']

            enrollment.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='enrollment',
                resource_id=enrollment_id,
                resource_name=f"选课ID: {enrollment_id}",
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的选课信息
            enrollment_schema = EnrollmentSchema()
            enrollment_data = enrollment_schema.dump(enrollment)

            return success_response("选课信息更新成功", enrollment_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@enrollments_ns.route('/<string:enrollment_id>/drop')
class EnrollmentDropResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('drop_enrollment')
    def post(self, enrollment_id):
        """学生退选"""
        try:
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return not_found_response("选课记录不存在")

            current_user_id = get_jwt_identity()

            # 检查权限：学生只能退选自己的课程
            if not g.current_user.has_permission('enrollment_management'):
                student = Student.query.filter_by(user_id=current_user_id).first()
                if not student or student.id != enrollment.student_id:
                    return forbidden_response("只能退选自己的课程")

            # 检查是否可以退选
            can_drop, message = enrollment.can_drop()
            if not can_drop:
                return error_response(message, 400)

            # 执行退选
            enrollment.drop_course("学生主动退选")

            # 更新课程选课人数
            if enrollment.course:
                enrollment.course.update_current_students()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='enrollment',
                resource_id=enrollment_id,
                resource_name=f"退选课程",
                old_values={'status': 'enrolled'},
                new_values={'status': 'dropped'}
            )

            return success_response("退选成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@enrollments_ns.route('/bulk')
class EnrollmentBulkResource(Resource):
    @jwt_required()
    @enrollments_ns.expect(bulk_enrollment_model)
    @enrollments_ns.doc('bulk_enrollment')
    @require_permission('enrollment_management')
    def post(self):
        """批量选课"""
        try:
            data = request.json
            course_id = data['course_id']
            student_ids = data['student_ids']
            semester = data['semester']
            enrollment_type = data.get('enrollment_type', 'regular')

            # 验证课程
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查课程容量
            if len(student_ids) > (course.max_students - course.current_students):
                return error_response(f"课程容量不足，剩余名额: {course.max_students - course.current_students}", 400)

            success_count = 0
            failed_enrollments = []

            for student_id in student_ids:
                try:
                    # 验证学生
                    student = Student.query.get(student_id)
                    if not student:
                        failed_enrollments.append(f"学生 {student_id} 不存在")
                        continue

                    # 检查是否已选过
                    existing = Enrollment.query.filter_by(
                        student_id=student_id,
                        course_id=course_id,
                        semester=semester
                    ).first()

                    if existing:
                        if existing.status == EnrollmentStatus.ENROLLED:
                            failed_enrollments.append(f"学生 {student.student_id} 已选过此课程")
                            continue
                        else:
                            # 重新激活
                            existing.status = EnrollmentStatus.ENROLLED
                            existing.save()
                            success_count += 1
                            continue

                    # 检查选课条件
                    can_enroll, message = course.can_student_enroll(student)
                    if not can_enroll:
                        failed_enrollments.append(f"学生 {student.student_id}: {message}")
                        continue

                    # 创建选课记录
                    enrollment = Enrollment(
                        student_id=student_id,
                        course_id=course_id,
                        semester=semester,
                        enrollment_type=enrollment_type,
                        status=EnrollmentStatus.ENROLLED
                    )
                    enrollment.save()
                    success_count += 1

                except Exception as e:
                    failed_enrollments.append(f"学生 {student_id}: {str(e)}")

            # 更新课程选课人数
            course.update_current_students()

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user_id=g.current_user.id,
                resource_type='enrollment',
                description=f"批量选课: 课程 {course.course_code}, 成功: {success_count}, 失败: {len(failed_enrollments)}"
            )

            response_data = {
                'success_count': success_count,
                'failed_count': len(failed_enrollments),
                'failed_enrollments': failed_enrollments,
                'course': {
                    'course_code': course.course_code,
                    'name': course.name,
                    'current_students': course.current_students,
                    'max_students': course.max_students
                }
            }

            return success_response("批量选课完成", response_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@enrollments.ns.route('/course/<string:course_id>/students')
@enrollments_ns.resource
class EnrollmentCourseStudentsResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('get_course_enrollments')
    def get(self, course_id):
        """获取课程选课学生列表"""
        try:
            # 验证课程
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查权限：授课教师或管理员
            current_user_id = get_jwt_identity()
            is_teacher = (g.current_user.role.value == 'teacher' and
                         course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_teacher or g.current_user.has_permission('enrollment_management')):
                return forbidden_response("权限不足")

            # 获取选课学生
            enrollments = db.session.query(Enrollment, Student, User).join(Student).join(User).filter(
                Enrollment.course_id == course_id,
                Enrollment.status == EnrollmentStatus.ENROLLED
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
                    'enrollment_type': enrollment.enrollment_type,
                    'enrollment_date': enrollment.enrollment_date.isoformat(),
                    'gpa': student.gpa
                }
                students_data.append(student_info)

            return success_response("获取课程选课学生成功", {
                'course': {
                    'course_code': course.course_code,
                    'name': course.name,
                    'current_students': course.current_students,
                    'max_students': course.max_students
                },
                'students': students_data
            })

        except Exception as e:
            return error_response(str(e), 500)

@enrollments.ns.route('/student/<string:student_id>/courses')
@enrollments_ns.resource
class EnrollmentStudentCoursesResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('get_student_enrollments')
    def get(self, student_id):
        """获取学生选课课程列表"""
        try:
            # 验证学生
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限：学生本人、辅导员或管理员
            current_user_id = get_jwt_identity()

            is_self = student.user_id == current_user_id
            is_advisor = (student.advisor_id == getattr(g.current_user, 'teacher_record', {}).id)
            has_permission = g.current_user.has_permission('enrollment_management')

            if not (is_self or is_advisor or has_permission):
                return forbidden_response("权限不足")

            # 获取选课课程
            enrollments = db.session.query(Enrollment, Course).join(Course).filter(
                Enrollment.student_id == student_id,
                Enrollment.status.in_([EnrollmentStatus.ENROLLED, EnrollmentStatus.COMPLETED])
            ).all()

            courses_data = []
            for enrollment, course in enrollments:
                course_info = {
                    'enrollment_id': enrollment.id,
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'semester': enrollment.semester,
                    'status': enrollment.status.value,
                    'enrollment_type': enrollment.enrollment_type,
                    'enrollment_date': enrollment.enrollment_date.isoformat(),
                    'teacher': None
                }

                if course.teacher and course.teacher.user and course.teacher.user.profile:
                    course_info['teacher'] = course.teacher.user.profile.full_name

                courses_data.append(course_info)

            return success_response("获取学生选课课程成功", {
                'student': {
                    'student_id': student.student_id,
                    'name': student.user.profile.full_name if student.user.profile else student.user.username,
                    'grade': student.grade,
                    'major': student.major
                },
                'courses': courses_data
            })

        except Exception as e:
            return error_response(str(e), 500)

@enrollments_ns.route('/stats')
class EnrollmentStatsResource(Resource):
    @jwt_required()
    @enrollments_ns.doc('get_enrollment_stats')
    @require_permission('enrollment_management')
    def get(self):
        """获取选课统计信息"""
        try:
            stats = {}

            # 基础统计
            stats['total_enrollments'] = Enrollment.query.count()
            stats['active_enrollments'] = Enrollment.query.filter_by(status=EnrollmentStatus.ENROLLED).count()
            stats['completed_enrollments'] = Enrollment.query.filter_by(status=EnrollmentStatus.COMPLETED).count()
            stats['dropped_enrollments'] = Enrollment.query.filter_by(status=EnrollmentStatus.DROPPED).count()

            # 按状态统计
            stats['enrollments_by_status'] = db.session.query(
                Enrollment.status, db.func.count(Enrollment.id)
            ).group_by(Enrollment.status).all()
            stats['enrollments_by_status'] = {
                status.value: count for status, count in stats['enrollments_by_status']
            }

            # 按学期统计
            stats['enrollments_by_semester'] = db.session.query(
                Enrollment.semester, db.func.count(Enrollment.id)
            ).group_by(Enrollment.semester).all()
            stats['enrollments_by_semester'] = dict(stats['enrollments_by_semester'])

            # 最热门的课程
            popular_courses = db.session.query(
                Course.course_code, Course.name, db.func.count(Enrollment.id).label('enrollment_count')
            ).join(Enrollment).filter(
                Enrollment.status == EnrollmentStatus.ENROLLED
            ).group_by(Course.id, Course.course_code, Course.name).order_by(
                db.func.count(Enrollment.id).desc()
            ).limit(10).all()

            stats['popular_courses'] = [
                {
                    'course_code': course.course_code,
                    'name': course.name,
                    'enrollment_count': course.enrollment_count
                }
                for course in popular_courses
            ]

            return success_response("获取选课统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)