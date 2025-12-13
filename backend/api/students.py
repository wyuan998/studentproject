# ========================================
# 学生信息管理系统 - 学生管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import csv
import io

from models import (
    Student, User, UserProfile, AcademicStatus,
    Course, Enrollment, Grade, Teacher,
    AuditLog, AuditAction
)
from schemas import (
    StudentSchema, StudentCreateSchema, StudentUpdateSchema,
    StudentSearchSchema, StudentStatsSchema,
    StudentImportSchema, StudentExportSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, not_found_response,
    forbidden_response, validation_error_response,
    make_file_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query
from utils.file_upload import save_uploaded_file, validate_file_type

# 创建命名空间
students_ns = Namespace('students', description='学生管理相关操作')

# 定义数据模型
student_create_model = students_ns.model('StudentCreate', {
    'student_id': fields.String(required=True, description='学号'),
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    'confirm_password': fields.String(required=True, description='确认密码'),
    'first_name': fields.String(required=True, description='姓'),
    'last_name': fields.String(required=True, description='名'),
    'grade': fields.String(required=True, description='年级'),
    'class_name': fields.String(required=True, description='班级'),
    'major': fields.String(required=True, description='专业'),
    'minor': fields.String(description='辅修专业'),
    'enrollment_date': fields.Date(required=True, description='入学日期'),
    'expected_graduation_date': fields.Date(description='预计毕业日期'),
    'academic_status': fields.String(description='学业状态', enum=['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave']),
    'phone': fields.String(description='手机号码'),
    'gender': fields.String(description='性别', enum=['male', 'female', 'other']),
    'birthday': fields.Date(description='生日'),
    'address': fields.String(description='地址')
})

student_update_model = students_ns.model('StudentUpdate', {
    'grade': fields.String(description='年级'),
    'class_name': fields.String(description='班级'),
    'major': fields.String(description='专业'),
    'minor': fields.String(description='辅修专业'),
    'expected_graduation_date': fields.Date(description='预计毕业日期'),
    'academic_status': fields.String(description='学业状态', enum=['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave']),
    'gpa': fields.Float(description='GPA'),
    'credits_earned': fields.Integer(description='已修学分'),
    'advisor_id': fields.String(description='辅导员ID'),
    'notes': fields.String(description='备注'),
    'phone': fields.String(description='手机号码'),
    'gender': fields.String(description='性别'),
    'birthday': fields.Date(description='生日'),
    'address': fields.String(description='地址'),
    'city': fields.String(description='城市'),
    'province': fields.String(description='省份')
})

student_search_model = students_ns.model('StudentSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'student_id': fields.String(description='学号'),
    'grade': fields.String(description='年级'),
    'class_name': fields.String(description='班级'),
    'major': fields.String(description='专业'),
    'academic_status': fields.String(description='学业状态'),
    'advisor_id': fields.String(description='辅导员ID'),
    'department': fields.String(description='院系'),
    'gpa_min': fields.Float(description='GPA最小值'),
    'gpa_max': fields.Float(description='GPA最大值'),
    'credits_min': fields.Integer(description='学分最小值'),
    'credits_max': fields.Integer(description='学分最大值'),
    'enrollment_start': fields.Date(description='入学开始日期'),
    'enrollment_end': fields.Date(description='入学结束日期'),
    'tags': fields.List(fields.String, description='标签'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='student_id'),
    'sort_order': fields.String(description='排序方式', default='asc')
})

@students_ns.route('')
class StudentListResource(Resource):
    @jwt_required()
    @students_ns.doc('list_students')
    @students_ns.expect(student_search_model)
    def get(self):
        """获取学生列表"""
        try:
            schema = StudentSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = Student.query.join(User).join(UserProfile)

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.filter(
                    or_(
                        Student.student_id.like(keyword),
                        User.username.like(keyword),
                        UserProfile.first_name.like(keyword),
                        UserProfile.last_name.like(keyword),
                        UserProfile.phone.like(keyword)
                    )
                )

            # 学号筛选
            if data.get('student_id'):
                query = query.filter(Student.student_id.like(f"%{data['student_id']}%"))

            # 年级筛选
            if data.get('grade'):
                query = query.filter(Student.grade == data['grade'])

            # 班级筛选
            if data.get('class_name'):
                query = query.filter(Student.class_name.like(f"%{data['class_name']}%"))

            # 专业筛选
            if data.get('major'):
                query = query.filter(Student.major.like(f"%{data['major']}%"))

            # 学业状态筛选
            if data.get('academic_status'):
                query = query.filter(Student.academic_status == AcademicStatus(data['academic_status']))

            # 辅导员筛选
            if data.get('advisor_id'):
                query = query.filter(Student.advisor_id == data['advisor_id'])

            # 部门筛选
            if data.get('department'):
                query = query.filter(UserProfile.department.like(f"%{data['department']}%"))

            # GPA范围筛选
            if data.get('gpa_min') is not None:
                query = query.filter(Student.gpa >= data['gpa_min'])
            if data.get('gpa_max') is not None:
                query = query.filter(Student.gpa <= data['gpa_max'])

            # 学分范围筛选
            if data.get('credits_min') is not None:
                query = query.filter(Student.credits_earned >= data['credits_min'])
            if data.get('credits_max') is not None:
                query = query.filter(Student.credits_earned <= data['credits_max'])

            # 入学时间范围筛选
            if data.get('enrollment_start'):
                query = query.filter(Student.enrollment_date >= data['enrollment_start'])
            if data.get('enrollment_end'):
                query = query.filter(Student.enrollment_date <= data['enrollment_end'])

            # 标签筛选
            if data.get('tags'):
                for tag in data['tags']:
                    query = query.filter(Student.tags.like(f'%{tag}%'))

            # 排序
            sort_field_map = {
                'student_id': Student.student_id,
                'grade': Student.grade,
                'class_name': Student.class_name,
                'major': Student.major,
                'gpa': Student.gpa,
                'credits_earned': Student.credits_earned,
                'enrollment_date': Student.enrollment_date
            }

            sort_field = sort_field_map.get(data['sort_by'], Student.student_id)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            students = pagination.items

            # 序列化
            student_schema = StudentSchema(many=True)
            student_data = student_schema.dump(students)

            response_data = {
                'students': student_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取学生列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @students_ns.expect(student_create_model)
    @students_ns.doc('create_student')
    @require_permission('student_management')
    @rate_limit("10/minute")
    def post(self):
        """创建学生"""
        try:
            schema = StudentCreateSchema()
            data = schema.load(request.json)

            # 检查学号唯一性
            if Student.query.filter_by(student_id=data['student_id']).first():
                return error_response("学号已存在", 400)

            # 检查用户名和邮箱唯一性
            if User.query.filter_by(username=data['username']).first():
                return error_response("用户名已存在", 400)

            if User.query.filter_by(email=data['email']).first():
                return error_response("邮箱已存在", 400)

            # 验证辅导员
            advisor = None
            if data.get('advisor_id'):
                advisor = Teacher.query.filter_by(id=data['advisor_id']).first()
                if not advisor:
                    return error_response("指定的辅导员不存在", 400)

            # 创建用户
            user = User(
                username=data['username'],
                email=data['email'],
                role='student',
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
                birthday=data.get('birthday'),
                address=data.get('address')
            )
            profile.save()

            # 创建学生记录
            student = Student(
                user_id=user.id,
                student_id=data['student_id'],
                grade=data['grade'],
                class_name=data['class_name'],
                major=data['major'],
                minor=data.get('minor'),
                enrollment_date=data['enrollment_date'],
                expected_graduation_date=data.get('expected_graduation_date'),
                academic_status=AcademicStatus(data.get('academic_status', 'enrolled')),
                advisor_id=data.get('advisor_id')
            )
            student.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=g.current_user.id,
                resource_type='student',
                resource_id=student.id,
                resource_name=f"{data['student_id']} - {data['first_name']} {data['last_name']}"
            )

            # 返回学生信息
            student_schema = StudentSchema()
            student_data = student_schema.dump(student)

            return success_response("学生创建成功", student_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@students_ns.route('/<string:student_id>')
class StudentResource(Resource):
    @jwt_required()
    @students_ns.doc('get_student')
    def get(self, student_id):
        """获取学生详情"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限：本人、辅导员或有student_management权限
            current_user_id = get_jwt_identity()
            if (current_user_id != student.user_id and
                not g.current_user.has_permission('student_management') and
                not (g.current_user.role.value == 'teacher' and
                     hasattr(g.current_user, 'teacher_record') and
                     g.current_user.teacher_record.id == student.advisor_id)):
                return forbidden_response("权限不足")

            # 序列化
            student_schema = StudentSchema()
            student_data = student_schema.dump(student)

            return success_response("获取学生信息成功", student_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @students_ns.expect(student_update_model)
    @students_ns.doc('update_student')
    def put(self, student_id):
        """更新学生信息"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_self = current_user_id == student.user_id
            has_permission = g.current_user.has_permission('student_management')
            is_advisor = (g.current_user.role.value == 'teacher' and
                         hasattr(g.current_user, 'teacher_record') and
                         g.current_user.teacher_record.id == student.advisor_id)

            if not (is_self or has_permission or is_advisor):
                return forbidden_response("权限不足")

            schema = StudentUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新学生基本信息
            updatable_fields = [
                'grade', 'class_name', 'major', 'minor', 'expected_graduation_date',
                'academic_status', 'gpa', 'credits_earned', 'advisor_id', 'notes'
            ]

            # 只有管理员和辅导员可以修改部分字段
            admin_only_fields = ['academic_status', 'gpa', 'credits_earned', 'advisor_id']

            for field in updatable_fields:
                if field in data:
                    if field in admin_only_fields and not (has_permission or is_advisor):
                        continue

                    old_value = getattr(student, field)
                    new_value = data[field]

                    if old_value != new_value:
                        old_values[field] = old_value
                        setattr(student, field, new_value)
                        new_values[field] = new_value

            # 更新用户资料（本人或管理员）
            if is_self or has_permission:
                profile_fields = ['phone', 'gender', 'birthday', 'address', 'city', 'province']

                if student.profile:
                    for field in profile_fields:
                        if field in data:
                            old_value = getattr(student.profile, field)
                            new_value = data[field]

                            if old_value != new_value:
                                old_values[f'profile_{field}'] = old_value
                                setattr(student.profile, field, new_value)
                                new_values[f'profile_{field}'] = new_value

            student.save()
            if student.profile:
                student.profile.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='student',
                resource_id=student_id,
                resource_name=student.student_id,
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的学生信息
            student_schema = StudentSchema()
            student_data = student_schema.dump(student)

            return success_response("学生信息更新成功", student_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @jwt_required()
    @students_ns.doc('delete_student')
    @require_permission('student_management')
    def delete(self, student_id):
        """删除学生"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查是否可以删除
            if student.enrollments:
                return error_response("该学生有选课记录，无法删除", 400)

            # 记录审计日志
            AuditLog.log_delete(
                user_id=g.current_user.id,
                resource_type='student',
                resource_id=student_id,
                resource_name=student.student_id
            )

            # 删除学生（级联删除相关数据）
            db.session.delete(student)
            db.session.commit()

            return success_response("学生删除成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@students_ns.route('/<string:student_id>/courses')
class StudentCoursesResource(Resource):
    @jwt_required()
    @students_ns.doc('get_student_courses')
    def get(self, student_id):
        """获取学生课程列表"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            if (current_user_id != student.user_id and
                not g.current_user.has_permission('student_management')):
                return forbidden_response("权限不足")

            # 获取选课记录
            enrollments = db.session.query(Enrollment, Course).join(Course).filter(
                Enrollment.student_id == student_id
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
                    'enrollment_date': enrollment.enrollment_date.isoformat(),
                    'teacher': None
                }

                if course.teacher and course.teacher.user and course.teacher.user.profile:
                    course_info['teacher'] = course.teacher.user.profile.full_name

                courses_data.append(course_info)

            return success_response("获取学生课程列表成功", courses_data)

        except Exception as e:
            return error_response(str(e), 500)

@students_ns.route('/<string:student_id>/grades')
class StudentGradesResource(Resource):
    @jwt_required()
    @students_ns.doc('get_student_grades')
    def get(self, student_id):
        """获取学生成绩列表"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限
            current_user_id = get_jwt_identity()
            is_self = current_user_id == student.user_id
            has_permission = g.current_user.has_permission('grade_management')
            is_teacher = g.current_user.role.value == 'teacher'

            if not (is_self or has_permission or is_teacher):
                return forbidden_response("权限不足")

            # 获取成绩记录
            grades = db.session.query(Grade, Course).join(Course).filter(
                Grade.student_id == student_id
            ).order_by(Grade.created_at.desc()).all()

            grades_data = []
            for grade, course in grades:
                grade_info = {
                    'grade_id': grade.id,
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'exam_type': grade.exam_type.value,
                    'exam_name': grade.exam_name,
                    'score': grade.score,
                    'max_score': grade.max_score,
                    'percentage': grade.percentage,
                    'letter_grade': grade.letter_grade,
                    'grade_point': grade.grade_point,
                    'is_passing': grade.is_passing,
                    'graded_at': grade.graded_at.isoformat() if grade.graded_at else None,
                    'semester': grade.semester
                }
                grades_data.append(grade_info)

            return success_response("获取学生成绩列表成功", grades_data)

        except Exception as e:
            return error_response(str(e), 500)

@students_ns.route('/<string:student_id>/gpa')
class StudentGPAResource(Resource):
    @jwt_required()
    @students_ns.doc('update_student_gpa')
    def post(self, student_id):
        """更新学生GPA"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限
            if not g.current_user.has_permission('grade_management'):
                return forbidden_response("权限不足")

            # 更新GPA
            student.update_gpa()

            return success_response("GPA更新成功", {
                'student_id': student_id,
                'gpa': student.gpa
            })

        except Exception as e:
            return error_response(str(e), 500)

@students_ns.route('/<string:student_id>/graduate')
class StudentGraduateResource(Resource):
    @jwt_required()
    @students_ns.doc('graduate_student')
    @require_permission('student_management')
    def post(self, student_id):
        """学生毕业"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            data = request.json
            graduation_date = data.get('graduation_date')
            final_gpa = data.get('final_gpa')
            final_credits = data.get('final_credits')

            if not graduation_date or final_gpa is None or final_credits is None:
                return error_response("缺少必要参数", 400)

            # 更新学生信息
            student.academic_status = AcademicStatus.GRADUATED
            student.gpa = final_gpa
            student.credits_earned = final_credits

            # 记录审计日志
            AuditLog.log_update(
                user_id=g.current_user.id,
                resource_type='student',
                resource_id=student_id,
                resource_name=student.student_id,
                old_values={'academic_status': student.academic_status.value},
                new_values={'academic_status': 'graduated', 'gpa': final_gpa, 'credits_earned': final_credits}
            )

            return success_response("学生毕业信息更新成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@students_ns.route('/import')
class StudentImportResource(Resource):
    @jwt_required()
    @students_ns.doc('import_students')
    @require_permission('student_management')
    def post(self):
        """批量导入学生"""
        try:
            if 'file' not in request.files:
                return error_response("请选择文件", 400)

            file = request.files['file']
            if file.filename == '':
                return error_response("请选择文件", 400)

            # 验证文件类型
            if not validate_file_type(file.filename, ['csv', 'xlsx', 'xls']):
                return error_response("不支持的文件格式", 400)

            # 保存文件
            file_path = save_uploaded_file(file, 'imports')

            # 这里应该解析Excel/CSV文件并创建学生记录
            # 为了简化，这里只返回成功消息
            # 实际实现需要解析文件内容

            return success_response("学生导入功能正在开发中")

        except Exception as e:
            return error_response(str(e), 500)

@students_ns.route('/export')
class StudentExportResource(Resource):
    @jwt_required()
    @students_ns.doc('export_students')
    @require_permission('student_management')
    def get(self):
        """导出学生数据"""
        try:
            # 获取筛选条件
            grade = request.args.get('grade')
            major = request.args.get('major')
            academic_status = request.args.get('academic_status')
            format_type = request.args.get('format', 'excel')

            # 构建查询
            query = Student.query.join(User).join(UserProfile)

            if grade:
                query = query.filter(Student.grade == grade)
            if major:
                query = query.filter(Student.major.like(f"%{major}%"))
            if academic_status:
                query = query.filter(Student.academic_status == AcademicStatus(academic_status))

            students = query.all()

            # 生成CSV数据
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入标题
            writer.writerow([
                '学号', '姓名', '年级', '班级', '专业', '状态',
                'GPA', '已修学分', '入学日期', '手机号', '邮箱'
            ])

            # 写入数据
            for student in students:
                writer.writerow([
                    student.student_id,
                    student.user.profile.full_name if student.user.profile else student.user.username,
                    student.grade,
                    student.class_name,
                    student.major,
                    student.academic_status.value,
                    student.gpa or '',
                    student.credits_earned,
                    student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else '',
                    student.user.profile.phone if student.user.profile else '',
                    student.user.email
                ])

            # 创建文件响应
            csv_data = output.getvalue()
            output.close()

            filename = f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return make_file_response(csv_data, filename, 'text/csv')

        except Exception as e:
            return error_response(str(e), 500)

@students_ns.route('/stats')
class StudentStatsResource(Resource):
    @jwt_required()
    @students_ns.doc('get_student_stats')
    @require_permission('student_management')
    def get(self):
        """获取学生统计信息"""
        try:
            stats = {}

            # 基础统计
            stats['total_students'] = Student.query.count()
            stats['active_students'] = Student.query.filter_by(academic_status=AcademicStatus.ENROLLED).count()
            stats['graduated_students'] = Student.query.filter_by(academic_status=AcademicStatus.GRADUATED).count()
            stats['suspended_students'] = Student.query.filter_by(academic_status=AcademicStatus.SUSPENDED).count()
            stats['on_leave_students'] = Student.query.filter_by(academic_status=AcademicStatus.ON_LEAVE).count()

            # 按年级统计
            stats['students_by_grade'] = db.session.query(
                Student.grade, db.func.count(Student.id)
            ).group_by(Student.grade).all()
            stats['students_by_grade'] = dict(stats['students_by_grade'])

            # 按专业统计
            stats['students_by_major'] = db.session.query(
                Student.major, db.func.count(Student.id)
            ).group_by(Student.major).all()
            stats['students_by_major'] = dict(stats['students_by_major'])

            # GPA分布
            gpa_ranges = [
                ('3.5-4.0', Student.gpa >= 3.5),
                ('3.0-3.5', Student.gpa >= 3.0, Student.gpa < 3.5),
                ('2.5-3.0', Student.gpa >= 2.5, Student.gpa < 3.0),
                ('2.0-2.5', Student.gpa >= 2.0, Student.gpa < 2.5),
                ('0-2.0', Student.gpa < 2.0)
            ]

            stats['gpa_distribution'] = {}
            for label, condition in gpa_ranges:
                if len(condition) == 2:
                    count = Student.query.filter(condition[0], condition[1]).count()
                else:
                    count = Student.query.filter(condition).count()
                stats['gpa_distribution'][label] = count

            # 平均GPA
            avg_gpa = db.session.query(db.func.avg(Student.gpa)).filter(
                Student.gpa.isnot(None)
            ).scalar()
            stats['average_gpa'] = round(avg_gpa, 2) if avg_gpa else 0

            return success_response("获取学生统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)