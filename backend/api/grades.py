# ========================================
# 学生信息管理系统 - 成绩管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import csv
import io

from models import (
    Grade, Student, Course, User, UserProfile, Teacher,
    GradeType, Enrollment, AuditLog, AuditAction
)
from schemas import (
    GradeSchema, GradeCreateSchema, GradeUpdateSchema,
    GradeSearchSchema
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
grades_ns = Namespace('grades', description='成绩管理相关操作')

# 定义数据模型
grade_create_model = grades_ns.model('GradeCreate', {
    'student_id': fields.String(required=True, description='学生ID'),
    'course_id': fields.String(required=True, description='课程ID'),
    'exam_type': fields.String(required=True, description='考试类型', enum=['quiz', 'assignment', 'midterm', 'final', 'project', 'presentation', 'participation', 'lab', 'attendance', 'other']),
    'exam_name': fields.String(required=True, description='考试名称'),
    'score': fields.Float(required=True, description='分数'),
    'max_score': fields.Float(description='满分', default=100),
    'weight': fields.Float(description='权重'),
    'semester': fields.String(required=True, description='学期'),
    'comments': fields.String(description='评语'),
    'improvement_suggestions': fields.String(description='改进建议')
})

grade_update_model = grades_ns.model('GradeUpdate', {
    'score': fields.Float(description='分数'),
    'max_score': fields.Float(description='满分'),
    'weight': fields.Float(description='权重'),
    'comments': fields.String(description='评语'),
    'improvement_suggestions': fields.String(description='改进建议'),
    'is_published': fields.Boolean(description='是否发布'),
    'is_locked': fields.Boolean(description='是否锁定')
})

grade_search_model = grades_ns.model('GradeSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'student_id': fields.String(description='学生ID'),
    'course_id': fields.String(description='课程ID'),
    'teacher_id': fields.String(description='教师ID'),
    'exam_type': fields.String(description='考试类型'),
    'semester': fields.String(description='学期'),
    'score_min': fields.Float(description='分数最小值'),
    'score_max': fields.Float(description='分数最大值'),
    'is_published': fields.Boolean(description='是否已发布'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='created_at'),
    'sort_order': fields.String(description='排序方式', default='desc')
})

bulk_grade_model = grades_ns.model('BulkGrade', {
    'course_id': fields.String(required=True, description='课程ID'),
    'exam_type': fields.String(required=True, description='考试类型'),
    'exam_name': fields.String(required=True, description='考试名称'),
    'max_score': fields.Float(required=True, description='满分'),
    'weight': fields.Float(description='权重'),
    'semester': fields.String(required=True, description='学期'),
    'grades': fields.List(fields.Raw, required=True, description='成绩列表')
})

@grades_ns.route('')
class GradeListResource(Resource):
    @jwt_required()
    @grades_ns.doc('list_grades')
    @grades_ns.expect(grade_search_model)
    def get(self):
        """获取成绩列表"""
        try:
            schema = GradeSearchSchema()
            data = schema.load(request.args)

            # 构建查询
            query = Grade.query

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
                        Course.name.like(keyword),
                        Grade.exam_name.like(keyword)
                    )
                )

            # 学生筛选
            if data.get('student_id'):
                query = query.filter(Grade.student_id == data['student_id'])

            # 课程筛选
            if data.get('course_id'):
                query = query.filter(Grade.course_id == data['course_id'])

            # 教师筛选
            if data.get('teacher_id'):
                query = query.filter(Course.teacher_id == data['teacher_id'])

            # 考试类型筛选
            if data.get('exam_type'):
                query = query.filter(Grade.exam_type == GradeType(data['exam_type']))

            # 学期筛选
            if data.get('semester'):
                query = query.filter(Grade.semester.like(f"%{data['semester']}%"))

            # 分数范围筛选
            if data.get('score_min') is not None:
                query = query.filter(Grade.score >= data['score_min'])
            if data.get('score_max') is not None:
                query = query.filter(Grade.score <= data['score_max'])

            # 发布状态筛选
            if data.get('is_published') is not None:
                query = query.filter(Grade.is_published == data['is_published'])

            # 排序
            sort_field_map = {
                'created_at': Grade.created_at,
                'score': Grade.score,
                'exam_type': Grade.exam_type,
                'semester': Grade.semester,
                'student_id': Student.student_id,
                'course_code': Course.course_code
            }

            sort_field = sort_field_map.get(data['sort_by'], Grade.created_at)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            grades = pagination.items

            # 序列化
            grade_schema = GradeSchema(many=True)
            grade_data = grade_schema.dump(grades)

            response_data = {
                'grades': grade_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取成绩列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @grades_ns.expect(grade_create_model)
    @grades_ns.doc('create_grade')
    @rate_limit("20/minute")
    def post(self):
        """创建成绩记录"""
        try:
            schema = GradeCreateSchema()
            data = schema.load(request.json)

            current_user_id = get_jwt_identity()

            # 验证学生和课程
            student = Student.query.get(data['student_id'])
            if not student:
                return not_found_response("学生不存在")

            course = Course.query.get(data['course_id'])
            if not course:
                return not_found_response("课程不存在")

            # 检查权限：授课教师或管理员
            is_teacher = (g.current_user.role.value == 'teacher' and
                         course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            # 验证分数范围
            max_score = data.get('max_score', 100)
            if data['score'] < 0 or data['score'] > max_score:
                return error_response(f"分数必须在0-{max_score}之间", 400)

            # 检查是否有选课记录
            enrollment = Enrollment.query.filter_by(
                student_id=data['student_id'],
                course_id=data['course_id'],
                semester=data['semester']
            ).first()

            if not enrollment:
                return error_response("学生未选修此课程", 400)

            # 创建成绩记录
            grade = Grade(
                student_id=data['student_id'],
                course_id=data['course_id'],
                exam_type=GradeType(data['exam_type']),
                exam_name=data['exam_name'],
                score=data['score'],
                max_score=max_score,
                weight=data.get('weight', 1.0),
                semester=data['semester'],
                graded_by=current_user_id,
                graded_at=datetime.utcnow(),
                comments=data.get('comments'),
                improvement_suggestions=data.get('improvement_suggestions')
            )
            grade.save()

            # 计算班级统计
            grade.calculate_class_statistics()

            # 记录审计日志
            AuditLog.log_create(
                user_id=current_user_id,
                resource_type='grade',
                resource_id=grade.id,
                resource_name=f"{student.student_id} - {course.course_code} {data['exam_name']}"
            )

            # 返回成绩信息
            grade_schema = GradeSchema()
            grade_data = grade_schema.dump(grade)

            return success_response("成绩记录创建成功", grade_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@grades_ns.route('/<string:grade_id>')
class GradeResource(Resource):
    @jwt_required()
    @grades_ns.doc('get_grade')
    def get(self, grade_id):
        """获取成绩详情"""
        try:
            grade = Grade.query.get(grade_id)
            if not grade:
                return not_found_response("成绩记录不存在")

            # 检查权限：学生本人、授课教师或管理员
            current_user_id = get_jwt_identity()

            # 检查是否是学生本人
            student = Student.query.filter_by(user_id=current_user_id).first()
            is_student = student and student.id == grade.student_id

            # 检查是否是授课教师
            is_teacher = (g.current_user.role.value == 'teacher' and
                         grade.course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_student or is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            # 序列化
            grade_schema = GradeSchema()
            grade_data = grade_schema.dump(grade)

            return success_response("获取成绩详情成功", grade_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @grades_ns.expect(grade_update_model)
    @grades_ns.doc('update_grade')
    def put(self, grade_id):
        """更新成绩记录"""
        try:
            grade = Grade.query.get(grade_id)
            if not grade:
                return not_found_response("成绩记录不存在")

            # 检查权限：只有授课教师或管理员可以修改
            is_teacher = (g.current_user.role.value == 'teacher' and
                         grade.course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            # 检查是否已锁定
            if grade.is_locked:
                return error_response("成绩已锁定，无法修改", 400)

            schema = GradeUpdateSchema()
            data = schema.load(request.json)

            # 记录旧值用于审计
            old_values = {}
            new_values = {}

            # 更新成绩信息
            if data.get('score') is not None:
                max_score = data.get('max_score', grade.max_score)
                if data['score'] < 0 or data['score'] > max_score:
                    return error_response(f"分数必须在0-{max_score}之间", 400)

                old_values['score'] = grade.score
                grade.score = data['score']
                new_values['score'] = data['score']

            if data.get('max_score') is not None:
                old_values['max_score'] = grade.max_score
                grade.max_score = data['max_score']
                new_values['max_score'] = data['max_score']

            if data.get('weight') is not None:
                old_values['weight'] = grade.weight
                grade.weight = data['weight']
                new_values['weight'] = data['weight']

            if data.get('comments') is not None:
                old_values['comments'] = grade.comments
                grade.comments = data['comments']
                new_values['comments'] = data['comments']

            if data.get('improvement_suggestions') is not None:
                old_values['improvement_suggestions'] = grade.improvement_suggestions
                grade.improvement_suggestions = data['improvement_suggestions']
                new_values['improvement_suggestions'] = data['improvement_suggestions']

            if data.get('is_published') is not None:
                old_values['is_published'] = grade.is_published
                grade.is_published = data['is_published']
                new_values['is_published'] = data['is_published']

                if data['is_published'] and not grade.published_at:
                    grade.published_at = datetime.utcnow()

            if data.get('is_locked') is not None:
                old_values['is_locked'] = grade.is_locked
                grade.is_locked = data['is_locked']
                new_values['is_locked'] = data['is_locked']

                if data['is_locked'] and not grade.locked_at:
                    grade.locked_at = datetime.utcnow()

            grade.save()

            # 重新计算班级统计
            grade.calculate_class_statistics()

            # 记录审计日志
            AuditLog.log_update(
                user_id=get_jwt_identity(),
                resource_type='grade',
                resource_id=grade_id,
                resource_name=grade.exam_name,
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )

            # 返回更新后的成绩信息
            grade_schema = GradeSchema()
            grade_data = grade_schema.dump(grade)

            return success_response("成绩记录更新成功", grade_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@grades_ns.route('/<string:grade_id>/publish')
class GradePublishResource(Resource):
    @jwt_required()
    @grades_ns.doc('publish_grade')
    def post(self, grade_id):
        """发布成绩"""
        try:
            grade = Grade.query.get(grade_id)
            if not grade:
                return not_found_response("成绩记录不存在")

            # 检查权限
            is_teacher = (g.current_user.role.value == 'teacher' and
                         grade.course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            if grade.is_published:
                return error_response("成绩已发布", 400)

            grade.publish()

            # 记录审计日志
            AuditLog.log_update(
                user_id=get_jwt_identity(),
                resource_type='grade',
                resource_id=grade_id,
                resource_name=grade.exam_name,
                old_values={'is_published': False},
                new_values={'is_published': True}
            )

            return success_response("成绩发布成功")

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/<string:grade_id>/lock')
class GradeLockResource(Resource):
    @jwt_required()
    @grades_ns.doc('lock_grade')
    def post(self, grade_id):
        """锁定成绩"""
        try:
            grade = Grade.query.get(grade_id)
            if not grade:
                return not_found_response("成绩记录不存在")

            # 检查权限
            if not g.current_user.has_permission('grade_management'):
                return forbidden_response("权限不足")

            if grade.is_locked:
                return error_response("成绩已锁定", 400)

            grade.lock()

            # 记录审计日志
            AuditLog.log_update(
                user_id=get_jwt_identity(),
                resource_type='grade',
                resource_id=grade_id,
                resource_name=grade.exam_name,
                old_values={'is_locked': False},
                new_values={'is_locked': True}
            )

            return success_response("成绩锁定成功")

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/bulk')
class GradeBulkResource(Resource):
    @jwt_required()
    @grades_ns.expect(bulk_grade_model)
    @grades_ns.doc('bulk_grade')
    @require_permission('grade_management')
    @rate_limit("10/minute")
    def post(self):
        """批量录入成绩"""
        try:
            data = request.json
            course_id = data['course_id']
            exam_type = data['exam_type']
            exam_name = data['exam_name']
            max_score = data['max_score']
            weight = data.get('weight', 1.0)
            semester = data['semester']
            grades_data = data['grades']

            # 验证课程
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            success_count = 0
            failed_grades = []

            for grade_data in grades_data:
                try:
                    student_id = grade_data.get('student_id')
                    score = grade_data.get('score')

                    if not student_id or score is None:
                        failed_grades.append(f"学生ID或分数缺失: {grade_data}")
                        continue

                    # 验证分数范围
                    if score < 0 or score > max_score:
                        failed_grades.append(f"学生 {student_id} 分数超出范围: {score}")
                        continue

                    # 验证学生
                    student = Student.query.get(student_id)
                    if not student:
                        failed_grades.append(f"学生 {student_id} 不存在")
                        continue

                    # 检查是否有选课记录
                    enrollment = Enrollment.query.filter_by(
                        student_id=student_id,
                        course_id=course_id,
                        semester=semester
                    ).first()

                    if not enrollment:
                        failed_grades.append(f"学生 {student.student_id} 未选修此课程")
                        continue

                    # 检查是否已存在相同记录
                    existing_grade = Grade.query.filter_by(
                        student_id=student_id,
                        course_id=course_id,
                        exam_type=GradeType(exam_type),
                        exam_name=exam_name,
                        semester=semester
                    ).first()

                    if existing_grade:
                        # 更新现有记录
                        existing_grade.score = score
                        existing_grade.max_score = max_score
                        existing_grade.weight = weight
                        existing_grade.graded_by = get_jwt_identity()
                        existing_grade.graded_at = datetime.utcnow()
                        existing_grade.save()
                        success_count += 1
                    else:
                        # 创建新记录
                        grade = Grade(
                            student_id=student_id,
                            course_id=course_id,
                            exam_type=GradeType(exam_type),
                            exam_name=exam_name,
                            score=score,
                            max_score=max_score,
                            weight=weight,
                            semester=semester,
                            graded_by=get_jwt_identity(),
                            graded_at=datetime.utcnow()
                        )
                        grade.save()
                        success_count += 1

                except Exception as e:
                    failed_grades.append(f"处理学生 {grade_data.get('student_id', 'unknown')} 时出错: {str(e)}")

            # 计算班级统计
            for grade_data in grades_data:
                if 'student_id' in grade_data:
                    grade = Grade.query.filter_by(
                        student_id=grade_data['student_id'],
                        course_id=course_id,
                        exam_type=GradeType(exam_type),
                        exam_name=exam_name,
                        semester=semester
                    ).first()
                    if grade:
                        grade.calculate_class_statistics()

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user_id=get_jwt_identity(),
                resource_type='grade',
                description=f"批量录入成绩: 课程 {course.course_code} {exam_name}, 成功: {success_count}, 失败: {len(failed_grades)}"
            )

            response_data = {
                'success_count': success_count,
                'failed_count': len(failed_grades),
                'failed_grades': failed_grades,
                'course': {
                    'course_code': course.course_code,
                    'name': course.name,
                    'exam_name': exam_name
                }
            }

            return success_response("批量录入成绩完成", response_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@grades_ns.route('/export')
class GradeExportResource(Resource):
    @jwt_required()
    @grades_ns.doc('export_grades')
    def get(self):
        """导出成绩数据"""
        try:
            # 获取筛选条件
            course_id = request.args.get('course_id')
            semester = request.args.get('semester')
            exam_type = request.args.get('exam_type')
            format_type = request.args.get('format', 'csv')

            # 构建查询
            query = Grade.query.join(Student).join(User).join(Course)

            if course_id:
                query = query.filter(Grade.course_id == course_id)
            if semester:
                query = query.filter(Grade.semester.like(f"%{semester}%"))
            if exam_type:
                query = query.filter(Grade.exam_type == GradeType(exam_type))

            grades = query.order_by(Grade.student_id, Grade.exam_type).all()

            # 生成CSV数据
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入标题
            writer.writerow([
                '学号', '姓名', '课程代码', '课程名称', '考试类型',
                '考试名称', '分数', '满分', '百分比', '等级', '绩点',
                '是否及格', '学期', '评分时间'
            ])

            # 写入数据
            for grade in grades:
                writer.writerow([
                    grade.student.student_id,
                    grade.student.user.profile.full_name if grade.student.user.profile else grade.student.user.username,
                    grade.course.course_code,
                    grade.course.name,
                    grade.exam_type.value,
                    grade.exam_name,
                    grade.score,
                    grade.max_score,
                    f"{grade.percentage:.1f}%",
                    grade.letter_grade or '',
                    grade.grade_point or '',
                    '是' if grade.is_passing else '否',
                    grade.semester,
                    grade.graded_at.strftime('%Y-%m-%d %H:%M:%S') if grade.graded_at else ''
                ])

            # 创建文件响应
            csv_data = output.getvalue()
            output.close()

            filename = f"grades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return make_file_response(csv_data, filename, 'text/csv')

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/import')
class GradeImportResource(Resource):
    @jwt_required()
    @grades_ns.doc('import_grades')
    @require_permission('grade_management')
    def post(self):
        """导入成绩数据"""
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

            # 这里应该解析Excel/CSV文件并创建成绩记录
            # 为了简化，这里只返回成功消息
            # 实际实现需要解析文件内容

            return success_response("成绩导入功能正在开发中")

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/course/<string:course_id>/statistics')
class CourseGradeStatsResource(Resource):
    @jwt_required()
    @grades_ns.doc('get_course_grade_stats')
    def get(self, course_id):
        """获取课程成绩统计"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return not_found_response("课程不存在")

            # 检查权限：授课教师或管理员
            current_user_id = get_jwt_identity()
            is_teacher = (g.current_user.role.value == 'teacher' and
                         course.teacher_id == getattr(g.current_user, 'teacher_record', {}).id)

            if not (is_teacher or g.current_user.has_permission('grade_management')):
                return forbidden_response("权限不足")

            # 获取各类型考试统计
            exam_types = db.session.query(
                Grade.exam_type,
                db.func.count(Grade.id).label('total'),
                db.func.avg(Grade.score).label('average'),
                db.func.min(Grade.score).label('min_score'),
                db.func.max(Grade.score).label('max_score')
            ).filter_by(course_id=course_id).group_by(Grade.exam_type).all()

            stats = {
                'course_info': {
                    'course_code': course.course_code,
                    'name': course.name,
                    'credits': course.credits
                },
                'exam_statistics': []
            }

            for exam_type in exam_types:
                stats['exam_statistics'].append({
                    'exam_type': exam_type.exam_type.value,
                    'total_count': exam_type.total,
                    'average_score': round(exam_type.average, 2) if exam_type.average else 0,
                    'min_score': exam_type.min_score,
                    'max_score': exam_type.max_score
                })

            return success_response("获取课程成绩统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/student/<string:student_id>/summary')
class StudentGradeSummaryResource(Resource):
    @jwt_required()
    @grades_ns.doc('get_student_grade_summary')
    def get(self, student_id):
        """获取学生成绩汇总"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return not_found_response("学生不存在")

            # 检查权限：学生本人、辅导员或管理员
            current_user_id = get_jwt_identity()

            is_self = student.user_id == current_user_id
            is_advisor = (student.advisor_id == getattr(g.current_user, 'teacher_record', {}).id)
            has_permission = g.current_user.has_permission('grade_management')

            if not (is_self or is_advisor or has_permission):
                return forbidden_response("权限不足")

            # 获取成绩统计
            grades = db.session.query(Grade, Course).join(Course).filter(
                Grade.student_id == student_id
            ).all()

            summary = {
                'student_info': {
                    'student_id': student.student_id,
                    'name': student.user.profile.full_name if student.user.profile else student.user.username,
                    'major': student.major,
                    'grade': student.grade
                },
                'overall_stats': {
                    'total_courses': len(set([g.course_id for g, c in grades])),
                    'total_grades': len(grades),
                    'average_score': 0,
                    'passed_count': 0,
                    'failed_count': 0
                },
                'course_grades': []
            }

            # 按课程分组统计
            course_grades = {}
            for grade, course in grades:
                if course.id not in course_grades:
                    course_grades[course.id] = {
                        'course_code': course.course_code,
                        'course_name': course.name,
                        'credits': course.credits,
                        'grades': []
                    }

                grade_info = {
                    'exam_type': grade.exam_type.value,
                    'exam_name': grade.exam_name,
                    'score': grade.score,
                    'max_score': grade.max_score,
                    'percentage': grade.percentage,
                    'letter_grade': grade.letter_grade,
                    'grade_point': grade.grade_point,
                    'is_passing': grade.is_passing,
                    'semester': grade.semester
                }
                course_grades[course.id]['grades'].append(grade_info)

            # 计算整体统计
            total_score = 0
            total_count = 0
            passed_count = 0

            for grade, course in grades:
                if grade.score is not None:
                    total_score += grade.percentage
                    total_count += 1
                    if grade.is_passing:
                        passed_count += 1

            if total_count > 0:
                summary['overall_stats']['average_score'] = round(total_score / total_count, 2)
                summary['overall_stats']['passed_count'] = passed_count
                summary['overall_stats']['failed_count'] = total_count - passed_count
                summary['overall_stats']['pass_rate'] = round((passed_count / total_count) * 100, 2)

            summary['course_grades'] = list(course_grades.values())

            return success_response("获取学生成绩汇总成功", summary)

        except Exception as e:
            return error_response(str(e), 500)

@grades_ns.route('/statistics')
class GradeStatisticsResource(Resource):
    @jwt_required()
    @grades_ns.doc('get_grade_statistics')
    @require_permission('grade_management')
    def get(self):
        """获取成绩统计信息"""
        try:
            stats = {}

            # 基础统计
            stats['total_grades'] = Grade.query.count()
            stats['published_grades'] = Grade.query.filter_by(is_published=True).count()
            stats['unpublished_grades'] = Grade.query.filter_by(is_published=False).count()

            # 按考试类型统计
            stats['grades_by_type'] = db.session.query(
                Grade.exam_type, db.func.count(Grade.id)
            ).group_by(Grade.exam_type).all()
            stats['grades_by_type'] = {
                exam_type.value: count for exam_type, count in stats['grades_by_type']
            }

            # 按学期统计
            stats['grades_by_semester'] = db.session.query(
                Grade.semester, db.func.count(Grade.id)
            ).group_by(Grade.semester).all()
            stats['grades_by_semester'] = dict(stats['grades_by_semester'])

            # 平均分统计
            avg_scores = db.session.query(
                Grade.exam_type,
                db.func.avg(Grade.score).label('average')
            ).filter(Grade.score.isnot(None)).group_by(Grade.exam_type).all()

            stats['average_scores'] = {
                exam_type.exam_type.value: round(avg_score.average, 2) for exam_type, avg_score in avg_scores
            }

            # 及格率统计
            pass_rates = {}
            exam_types = db.session.query(Grade.exam_type).distinct().all()

            for exam_type in exam_types:
                total = Grade.query.filter_by(exam_type=exam_type.exam_type).count()
                passed = Grade.query.filter(
                    Grade.exam_type == exam_type.exam_type,
                    Grade.score >= 60
                ).count()

                if total > 0:
                    pass_rates[exam_type.exam_type.value] = round((passed / total) * 100, 2)

            stats['pass_rates'] = pass_rates

            # 成绩分布统计
            score_ranges = [
                ('90-100', Grade.score >= 90),
                ('80-89', Grade.score >= 80, Grade.score < 90),
                ('70-79', Grade.score >= 70, Grade.score < 80),
                ('60-69', Grade.score >= 60, Grade.score < 70),
                ('0-59', Grade.score < 60)
            ]

            stats['score_distribution'] = {}
            for label, condition in score_ranges:
                if len(condition) == 2:
                    count = Grade.query.filter(condition[0], condition[1]).count()
                else:
                    count = Grade.query.filter(condition).count()
                stats['score_distribution'][label] = count

            return success_response("获取成绩统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)