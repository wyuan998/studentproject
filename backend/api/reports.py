from flask import request, current_app, send_file
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import func, desc, or_, and_, extract
from datetime import datetime, timedelta
import io
import csv
import json

from ..models import User, Student, Teacher, Course, Enrollment, Grade, AuditLog, db
from ..utils.responses import success_response, error_response
from ..utils.decorators import require_permission
from ..schemas.student import StudentSchema
from ..schemas.teacher import TeacherSchema

api = Namespace('reports', description='报表统计管理')

# Swagger模型定义
report_filter_model = api.model('ReportFilter', {
    'start_date': fields.String(description='开始日期 (YYYY-MM-DD)'),
    'end_date': fields.String(description='结束日期 (YYYY-MM-DD)'),
    'department': fields.String(description='院系筛选'),
    'grade_level': fields.String(description='年级筛选'),
    'course_category': fields.String(description='课程类别筛选'),
    'semester': fields.String(description='学期筛选'),
    'teacher_id': fields.Integer(description='教师ID筛选')
})

export_model = api.model('ExportData', {
    'report_type': fields.String(required=True, description='报表类型'),
    'format': fields.String(required=True, description='导出格式 (csv/json/excel)'),
    'filters': fields.Raw(description='筛选条件')
})

# 初始化Schema
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)

@api.route('/dashboard')
class DashboardStats(Resource):
    @api.doc('get_dashboard_stats')
    @jwt_required()
    @require_permission('reports:view')
    def get(self):
        """获取仪表板统计数据"""
        try:
            # 基础统计
            total_students = Student.query.filter_by(is_active=True).count()
            total_teachers = Teacher.query.filter_by(is_active=True).count()
            total_courses = Course.query.filter_by(is_active=True).count()
            total_enrollments = Enrollment.query.count()

            # 本月新增统计
            current_month = datetime.utcnow().replace(day=1)
            new_students_this_month = Student.query.filter(
                Student.created_at >= current_month,
                Student.is_active == True
            ).count()

            new_teachers_this_month = Teacher.query.filter(
                Teacher.created_at >= current_month,
                Teacher.is_active == True
            ).count()

            # 课程统计
            active_courses = Course.query.filter_by(is_active=True).count()
            full_courses = db.session.query(Course.id)\
                                     .join(Enrollment)\
                                     .group_by(Course.id)\
                                     .having(func.count(Enrollment.id) >= Course.capacity)\
                                     .count()

            # 成绩统计
            grade_stats = db.session.query(
                func.avg(Grade.score).label('avg_score'),
                func.min(Grade.score).label('min_score'),
                func.max(Grade.score).label('max_score'),
                func.count(Grade.id).label('total_grades')
            ).first()

            # 在读学生按年级分布
            student_by_grade = db.session.query(
                Student.grade_level,
                func.count(Student.id).label('count')
            ).filter_by(is_active=True)\
             .group_by(Student.grade_level)\
             .order_by(Student.grade_level)\
             .all()

            # 教师按院系分布
            teacher_by_department = db.session.query(
                Teacher.department,
                func.count(Teacher.id).label('count')
            ).filter_by(is_active=True)\
             .group_by(Teacher.department)\
             .order_by(func.count(Teacher.id).desc())\
             .all()

            # 最近操作日志
            recent_logs = db.session.query(AuditLog, User.username)\
                                   .join(User, AuditLog.user_id == User.id)\
                                   .order_by(AuditLog.created_at.desc())\
                                   .limit(10)\
                                   .all()

            dashboard_data = {
                'overview': {
                    'total_students': total_students,
                    'total_teachers': total_teachers,
                    'total_courses': total_courses,
                    'total_enrollments': total_enrollments,
                    'new_students_this_month': new_students_this_month,
                    'new_teachers_this_month': new_teachers_this_month
                },
                'courses': {
                    'active_courses': active_courses,
                    'full_courses': full_courses,
                    'full_rate': round(full_courses / active_courses * 100, 2) if active_courses > 0 else 0
                },
                'grades': {
                    'average_score': round(float(grade_stats.avg_score), 2) if grade_stats.avg_score else 0,
                    'min_score': grade_stats.min_score,
                    'max_score': grade_stats.max_score,
                    'total_graded': grade_stats.total_grades
                },
                'distributions': {
                    'students_by_grade': [{'grade': grade, 'count': count} for grade, count in student_by_grade],
                    'teachers_by_department': [{'department': dept, 'count': count} for dept, count in teacher_by_department]
                },
                'recent_activities': [
                    {
                        'id': log.id,
                        'username': username,
                        'action': log.action,
                        'details': log.details,
                        'created_at': log.created_at.isoformat()
                    }
                    for log, username in recent_logs
                ]
            }

            return success_response(dashboard_data)

        except Exception as e:
            current_app.logger.error(f"获取仪表板统计失败: {str(e)}")
            return error_response("获取仪表板统计失败")

@api.route('/enrollments')
class EnrollmentReports(Resource):
    @api.doc('get_enrollment_reports')
    @api.expect(report_filter_model)
    @jwt_required()
    @require_permission('reports:view')
    def get(self):
        """获取选课报表数据"""
        try:
            # 获取筛选参数
            filters = request.get_json() or {}
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            department = filters.get('department')
            grade_level = filters.get('grade_level')
            course_category = filters.get('course_category')
            semester = filters.get('semester')

            # 构建基础查询
            query = db.session.query(
                Enrollment.id,
                Enrollment.status,
                Enrollment.created_at.label('enrollment_date'),
                Student.student_id.label('student_number'),
                Student.name.label('student_name'),
                Student.grade_level,
                Student.department.label('student_department'),
                Course.course_code,
                Course.name.label('course_name'),
                Course.credits,
                Course.category,
                Teacher.name.label('teacher_name'),
                Teacher.department.label('teacher_department'),
                Grade.score,
                Grade.grade_letter,
                Grade.semester.label('grade_semester')
            ).join(Student, Enrollment.student_id == Student.id)\
             .join(Course, Enrollment.course_id == Course.id)\
             .outerjoin(Teacher, Course.teacher_id == Teacher.id)\
             .outer_join(Grade, and_(
                 Grade.student_id == Student.id,
                 Grade.course_id == Course.id
             ))

            # 应用筛选条件
            if start_date:
                query = query.filter(Enrollment.created_at >= start_date)
            if end_date:
                query = query.filter(Enrollment.created_at <= end_date)
            if grade_level:
                query = query.filter(Student.grade_level == grade_level)
            if department:
                query = query.filter(or_(
                    Student.department == department,
                    Teacher.department == department
                ))
            if course_category:
                query = query.filter(Course.category == course_category)

            # 获取数据
            enrollments = query.order_by(Enrollment.created_at.desc()).all()

            # 统计数据
            total_enrollments = len(enrollments)
            pending_enrollments = len([e for e in enrollments if e.status == 'pending'])
            approved_enrollments = len([e for e in enrollments if e.status == 'approved'])
            rejected_enrollments = len([e for e in enrollments if e.status == 'rejected'])

            # 按课程统计选课人数
            course_stats = {}
            for e in enrollments:
                if e.course_name not in course_stats:
                    course_stats[e.course_name] = {
                        'course_code': e.course_code,
                        'teacher': e.teacher_name,
                        'total': 0,
                        'approved': 0,
                        'pending': 0,
                        'rejected': 0
                    }
                course_stats[e.course_name]['total'] += 1
                course_stats[e.course_name][e.status] += 1

            # 按院系统计选课情况
            dept_stats = {}
            for e in enrollments:
                dept = e.student_department or '未知'
                if dept not in dept_stats:
                    dept_stats[dept] = {'total': 0, 'approved': 0, 'pending': 0}
                dept_stats[dept]['total'] += 1
                dept_stats[dept][e.status] += 1

            # 格式化数据
            enrollment_data = [
                {
                    'id': e.id,
                    'enrollment_date': e.enrollment_date.isoformat(),
                    'student': {
                        'number': e.student_number,
                        'name': e.student_name,
                        'grade_level': e.grade_level,
                        'department': e.student_department
                    },
                    'course': {
                        'code': e.course_code,
                        'name': e.course_name,
                        'credits': e.credits,
                        'category': e.category,
                        'teacher': e.teacher_name
                    },
                    'status': e.status,
                    'grade': {
                        'score': e.score,
                        'letter': e.grade_letter,
                        'semester': e.grade_semester
                    } if e.score else None
                }
                for e in enrollments
            ]

            report_data = {
                'summary': {
                    'total_enrollments': total_enrollments,
                    'pending': pending_enrollments,
                    'approved': approved_enrollments,
                    'rejected': rejected_enrollments,
                    'approval_rate': round(approved_enrollments / total_enrollments * 100, 2) if total_enrollments > 0 else 0
                },
                'enrollments': enrollment_data,
                'course_statistics': course_stats,
                'department_statistics': dept_stats
            }

            return success_response(report_data)

        except Exception as e:
            current_app.logger.error(f"获取选课报表失败: {str(e)}")
            return error_response("获取选课报表失败")

@api.route('/grades')
class GradeReports(Resource):
    @api.doc('get_grade_reports')
    @api.expect(report_filter_model)
    @jwt_required()
    @require_permission('reports:view')
    def get(self):
        """获取成绩报表数据"""
        try:
            # 获取筛选参数
            filters = request.get_json() or {}
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            department = filters.get('department')
            grade_level = filters.get('grade_level')
            course_category = filters.get('course_category')
            semester = filters.get('semester')
            teacher_id = filters.get('teacher_id')

            # 构建基础查询
            query = db.session.query(
                Grade.id,
                Grade.score,
                Grade.grade_letter,
                Grade.gpa,
                Grade.semester,
                Grade.created_at.label('grade_date'),
                Student.student_id.label('student_number'),
                Student.name.label('student_name'),
                Student.grade_level,
                Student.department,
                Course.course_code,
                Course.name.label('course_name'),
                Course.credits,
                Course.category,
                Teacher.name.label('teacher_name')
            ).join(Student, Grade.student_id == Student.id)\
             .join(Course, Grade.course_id == Course.id)\
             .join(Teacher, Course.teacher_id == Teacher.id)

            # 应用筛选条件
            if start_date:
                query = query.filter(Grade.created_at >= start_date)
            if end_date:
                query = query.filter(Grade.created_at <= end_date)
            if grade_level:
                query = query.filter(Student.grade_level == grade_level)
            if department:
                query = query.filter(Student.department == department)
            if course_category:
                query = query.filter(Course.category == course_category)
            if semester:
                query = query.filter(Grade.semester == semester)
            if teacher_id:
                query = query.filter(Teacher.id == teacher_id)

            # 获取数据
            grades = query.order_by(Grade.created_at.desc()).all()

            # 统计数据
            total_grades = len(grades)
            if total_grades > 0:
                scores = [g.score for g in grades if g.score is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                max_score = max(scores) if scores else 0
                min_score = min(scores) if scores else 0

                # 成绩分布
                grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                for g in grades:
                    if g.grade_letter in grade_distribution:
                        grade_distribution[g.grade_letter] += 1
            else:
                avg_score = max_score = min_score = 0
                grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

            # 按课程统计成绩
            course_grade_stats = {}
            for g in grades:
                if g.course_name not in course_grade_stats:
                    course_grade_stats[g.course_name] = {
                        'course_code': g.course_code,
                        'teacher': g.teacher_name,
                        'total_students': 0,
                        'scores': [],
                        'avg_score': 0,
                        'grade_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                    }

                stats = course_grade_stats[g.course_name]
                stats['total_students'] += 1
                if g.score is not None:
                    stats['scores'].append(g.score)
                if g.grade_letter in stats['grade_distribution']:
                    stats['grade_distribution'][g.grade_letter] += 1

            # 计算各科平均分
            for course_name in course_grade_stats:
                scores = course_grade_stats[course_name]['scores']
                course_grade_stats[course_name]['avg_score'] = round(sum(scores) / len(scores), 2) if scores else 0
                del course_grade_stats[course_name]['scores']  # 删除原始分数列表

            # 按院系统计成绩
            dept_grade_stats = {}
            for g in grades:
                dept = g.department or '未知'
                if dept not in dept_grade_stats:
                    dept_grade_stats[dept] = {
                        'total_grades': 0,
                        'scores': [],
                        'avg_score': 0,
                        'grade_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                    }

                stats = dept_grade_stats[dept]
                stats['total_grades'] += 1
                if g.score is not None:
                    stats['scores'].append(g.score)
                if g.grade_letter in stats['grade_distribution']:
                    stats['grade_distribution'][g.grade_letter] += 1

            # 计算各院系平均分
            for dept in dept_grade_stats:
                scores = dept_grade_stats[dept]['scores']
                dept_grade_stats[dept]['avg_score'] = round(sum(scores) / len(scores), 2) if scores else 0
                del dept_grade_stats[dept]['scores']

            # 格式化数据
            grade_data = [
                {
                    'id': g.id,
                    'grade_date': g.grade_date.isoformat(),
                    'student': {
                        'number': g.student_number,
                        'name': g.student_name,
                        'grade_level': g.grade_level,
                        'department': g.department
                    },
                    'course': {
                        'code': g.course_code,
                        'name': g.course_name,
                        'credits': g.credits,
                        'category': g.category,
                        'teacher': g.teacher_name
                    },
                    'grade': {
                        'score': g.score,
                        'letter': g.grade_letter,
                        'gpa': g.gpa,
                        'semester': g.semester
                    }
                }
                for g in grades
            ]

            report_data = {
                'summary': {
                    'total_grades': total_grades,
                    'average_score': round(avg_score, 2),
                    'highest_score': max_score,
                    'lowest_score': min_score,
                    'grade_distribution': grade_distribution
                },
                'grades': grade_data,
                'course_statistics': course_grade_stats,
                'department_statistics': dept_grade_stats
            }

            return success_response(report_data)

        except Exception as e:
            current_app.logger.error(f"获取成绩报表失败: {str(e)}")
            return error_response("获取成绩报表失败")

@api.route('/teachers')
class TeacherReports(Resource):
    @api.doc('get_teacher_reports')
    @api.expect(report_filter_model)
    @jwt_required()
    @require_permission('reports:view')
    def get(self):
        """获取教师工作报表"""
        try:
            # 获取筛选参数
            filters = request.get_json() or {}
            department = filters.get('department')

            # 构建查询
            query = db.session.query(
                Teacher.id,
                Teacher.teacher_id,
                Teacher.name,
                Teacher.department,
                Teacher.title,
                Teacher.email,
                Teacher.phone,
                Teacher.workload,
                func.count(Course.id).label('course_count'),
                func.count(Enrollment.id).label('total_students'),
                func.avg(Grade.score).label('avg_grade'),
                func.count(distinct(Student.department)).label('student_departments')
            ).outerjoin(Course, Teacher.id == Course.teacher_id)\
             .outerjoin(Enrollment, Course.id == Enrollment.course_id)\
             .outerjoin(Grade, Course.id == Grade.course_id)\
             .outerjoin(Student, Grade.student_id == Student.id)\
             .filter(Teacher.is_active == True)\
             .group_by(Teacher.id)

            # 应用筛选
            if department:
                query = query.filter(Teacher.department == department)

            teachers = query.order_by(Teacher.department, Teacher.name).all()

            # 统计数据
            total_teachers = len(teachers)
            total_courses = sum(t.course_count for t in teachers)
            total_students = sum(t.total_students for t in teachers)

            # 按院系统计
            dept_stats = {}
            for t in teachers:
                dept = t.department or '未知'
                if dept not in dept_stats:
                    dept_stats[dept] = {
                        'teacher_count': 0,
                        'course_count': 0,
                        'student_count': 0,
                        'avg_workload': 0,
                        'avg_grade': 0
                    }
                dept_stats[dept]['teacher_count'] += 1
                dept_stats[dept]['course_count'] += t.course_count or 0
                dept_stats[dept]['student_count'] += t.total_students or 0

            # 计算院系平均数据
            for dept in dept_stats:
                teachers_in_dept = [t for t in teachers if t.department == dept]
                if teachers_in_dept:
                    dept_stats[dept]['avg_workload'] = round(
                        sum(t.workload or 0 for t in teachers_in_dept) / len(teachers_in_dept), 2
                    )
                    dept_stats[dept]['avg_grade'] = round(
                        sum(t.avg_grade or 0 for t in teachers_in_dept if t.avg_grade) /
                        len([t for t in teachers_in_dept if t.avg_grade]), 2
                    ) if any(t.avg_grade for t in teachers_in_dept) else 0

            # 格式化数据
            teacher_data = [
                {
                    'id': t.id,
                    'teacher_id': t.teacher_id,
                    'name': t.name,
                    'department': t.department,
                    'title': t.title,
                    'contact': {
                        'email': t.email,
                        'phone': t.phone
                    },
                    'workload': t.workload,
                    'statistics': {
                        'courses': t.course_count or 0,
                        'total_students': t.total_students or 0,
                        'average_grade': round(float(t.avg_grade), 2) if t.avg_grade else 0,
                        'student_departments': t.student_departments or 0
                    }
                }
                for t in teachers
            ]

            report_data = {
                'summary': {
                    'total_teachers': total_teachers,
                    'total_courses': total_courses,
                    'total_students': total_students
                },
                'teachers': teacher_data,
                'department_statistics': dept_stats
            }

            return success_response(report_data)

        except Exception as e:
            current_app.logger.error(f"获取教师报表失败: {str(e)}")
            return error_response("获取教师报表失败")

@api.route('/export')
class ReportExport(Resource):
    @api.doc('export_report')
    @api.expect(export_model)
    @jwt_required()
    @require_permission('reports:export')
    def post(self):
        """导出报表数据"""
        try:
            data = request.get_json()
            report_type = data.get('report_type')
            export_format = data.get('format', 'csv')
            filters = data.get('filters', {})

            if not report_type:
                return error_response("报表类型不能为空")

            # 根据报表类型获取数据
            if report_type == 'enrollments':
                report_data = self._get_enrollment_data(filters)
                filename = f"enrollments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            elif report_type == 'grades':
                report_data = self._get_grade_data(filters)
                filename = f"grades_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            elif report_type == 'teachers':
                report_data = self._get_teacher_data(filters)
                filename = f"teachers_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                return error_response("不支持的报表类型")

            # 根据格式导出
            if export_format == 'csv':
                return self._export_csv(report_data, filename)
            elif export_format == 'json':
                return self._export_json(report_data, filename)
            else:
                return error_response("不支持的导出格式")

        except Exception as e:
            current_app.logger.error(f"导出报表失败: {str(e)}")
            return error_response("导出报表失败")

    def _get_enrollment_data(self, filters):
        """获取选课数据"""
        query = db.session.query(
            Student.student_id,
            Student.name,
            Student.department.label('student_dept'),
            Course.course_code,
            Course.name,
            Course.credits,
            Teacher.name.label('teacher'),
            Enrollment.status,
            Enrollment.created_at
        ).join(Student, Enrollment.student_id == Student.id)\
         .join(Course, Enrollment.course_id == Course.id)\
         .outerjoin(Teacher, Course.teacher_id == Teacher.id)

        # 应用筛选
        if filters.get('start_date'):
            query = query.filter(Enrollment.created_at >= filters['start_date'])
        if filters.get('end_date'):
            query = query.filter(Enrollment.created_at <= filters['end_date'])
        if filters.get('department'):
            query = query.filter(Student.department == filters['department'])

        return query.all()

    def _get_grade_data(self, filters):
        """获取成绩数据"""
        query = db.session.query(
            Student.student_id,
            Student.name,
            Student.department,
            Course.course_code,
            Course.name,
            Course.credits,
            Teacher.name.label('teacher'),
            Grade.score,
            Grade.grade_letter,
            Grade.gpa,
            Grade.semester
        ).join(Student, Grade.student_id == Student.id)\
         .join(Course, Grade.course_id == Course.id)\
         .join(Teacher, Course.teacher_id == Teacher.id)

        # 应用筛选
        if filters.get('semester'):
            query = query.filter(Grade.semester == filters['semester'])
        if filters.get('department'):
            query = query.filter(Student.department == filters['department'])

        return query.all()

    def _get_teacher_data(self, filters):
        """获取教师数据"""
        query = db.session.query(
            Teacher.teacher_id,
            Teacher.name,
            Teacher.department,
            Teacher.title,
            Teacher.email,
            Teacher.workload
        ).filter(Teacher.is_active == True)

        # 应用筛选
        if filters.get('department'):
            query = query.filter(Teacher.department == filters['department'])

        return query.all()

    def _export_csv(self, data, filename):
        """导出CSV格式"""
        output = io.StringIO()

        if data and hasattr(data[0], '_fields'):
            # SQLAlchemy查询结果
            writer = csv.writer(output)
            writer.writerow(data[0]._fields)  # 写入表头

            for row in data:
                writer.writerow(row)

        # 生成文件
        output.seek(0)
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))  # 添加BOM以支持Excel中文
        mem.seek(0)

        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename}.csv'
        )

    def _export_json(self, data, filename):
        """导出JSON格式"""
        json_data = []

        if data and hasattr(data[0], '_fields'):
            # SQLAlchemy查询结果
            for row in data:
                row_dict = {}
                for field in row._fields:
                    value = getattr(row, field)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[field] = value
                json_data.append(row_dict)

        # 生成文件
        output = io.BytesIO()
        output.write(json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{filename}.json'
        )

@api.route('/statistics/overview')
class OverviewStatistics(Resource):
    @api.doc('get_overview_statistics')
    @jwt_required()
    @require_permission('reports:view')
    def get(self):
        """获取系统概览统计"""
        try:
            # 时间范围
            now = datetime.utcnow()
            this_month = now.replace(day=1)
            last_month = (this_month - timedelta(days=1)).replace(day=1)
            this_year = now.replace(month=1, day=1)

            # 用户统计
            total_users = User.query.filter_by(is_active=True).count()
            new_users_this_month = User.query.filter(
                User.created_at >= this_month,
                User.is_active == True
            ).count()

            # 学生统计
            total_students = Student.query.filter_by(is_active=True).count()
            active_enrollments = Enrollment.query.filter_by(status='approved').count()

            # 教师统计
            total_teachers = Teacher.query.filter_by(is_active=True).count()
            total_courses = Course.query.filter_by(is_active=True).count()

            # 成绩统计
            total_grades = Grade.query.count()
            recent_grades = Grade.query.filter(Grade.created_at >= this_month).count()

            # 操作日志统计
            recent_operations = AuditLog.query.filter(
                AuditLog.created_at >= this_month
            ).count()

            # 趋势数据（最近6个月）
            monthly_stats = []
            for i in range(6):
                month_start = (this_month - timedelta(days=30 * i)).replace(day=1)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                month_data = {
                    'month': month_start.strftime('%Y-%m'),
                    'new_students': Student.query.filter(
                        Student.created_at >= month_start,
                        Student.created_at <= month_end,
                        Student.is_active == True
                    ).count(),
                    'new_teachers': Teacher.query.filter(
                        Teacher.created_at >= month_start,
                        Teacher.created_at <= month_end,
                        Teacher.is_active == True
                    ).count(),
                    'new_courses': Course.query.filter(
                        Course.created_at >= month_start,
                        Course.created_at <= month_end,
                        Course.is_active == True
                    ).count(),
                    'new_enrollments': Enrollment.query.filter(
                        Enrollment.created_at >= month_start,
                        Enrollment.created_at <= month_end
                    ).count(),
                    'new_grades': Grade.query.filter(
                        Grade.created_at >= month_start,
                        Grade.created_at <= month_end
                    ).count()
                }
                monthly_stats.append(month_data)

            monthly_stats.reverse()  # 按时间正序

            overview_data = {
                'current_stats': {
                    'users': {
                        'total': total_users,
                        'new_this_month': new_users_this_month
                    },
                    'students': {
                        'total': total_students,
                        'active_enrollments': active_enrollments
                    },
                    'teachers': {
                        'total': total_teachers
                    },
                    'courses': {
                        'total': total_courses
                    },
                    'grades': {
                        'total': total_grades,
                        'new_this_month': recent_grades
                    },
                    'operations': {
                        'recent_count': recent_operations
                    }
                },
                'monthly_trends': monthly_stats
            }

            return success_response(overview_data)

        except Exception as e:
            current_app.logger.error(f"获取概览统计失败: {str(e)}")
            return error_response("获取概览统计失败")