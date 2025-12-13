# ========================================
# 学生信息管理系统 - 成绩服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_, func

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from .student_service import StudentService
from .course_service import CourseService
from .enrollment_service import EnrollmentService
from ..models import Grade, Student, Course, Enrollment, db
from ..utils.validators import AcademicValidator
from ..utils.logger import get_structured_logger
from ..utils.cache import cache_result


class GradeService(BaseService):
    """成绩服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Grade
        self.student_service = StudentService()
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService()

    # ========================================
    # 成绩管理
    # ========================================

    def create_grade(self, grade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建成绩记录

        Args:
            grade_data: 成绩数据

        Returns:
            Dict[str, Any]: 创建的成绩信息

        Raises:
            ServiceError: 创建失败
        """
        try:
            # 验证必填字段
            required_fields = ['student_id', 'course_id', 'score']
            for field in required_fields:
                if field not in grade_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证学生和课程存在
            student = self.student_service.get_by_id(grade_data['student_id'])
            if not student:
                raise ValidationError("学生不存在", 'student_id')

            course = self.course_service.get_by_id(grade_data['course_id'])
            if not course:
                raise ValidationError("课程不存在", 'course_id')

            # 检查权限（课程教师或管理员）
            current_user_id = self._get_current_user_id()
            if course.teacher_id != current_user_id:
                self._check_permission('grade_management')

            # 验证学生是否已选课且状态为approved
            enrollment = db.session.query(Enrollment).filter(
                and_(
                    Enrollment.student_id == grade_data['student_id'],
                    Enrollment.course_id == grade_data['course_id'],
                    Enrollment.status == 'approved'
                )
            ).first()

            if not enrollment:
                raise BusinessRuleError("学生未选课或选课未批准", 'no_valid_enrollment')

            # 验证成绩分数
            score_validation = AcademicValidator.validate_score(
                grade_data['score'],
                max_score=course.max_score or 100
            )
            if not score_validation['valid']:
                raise ValidationError(score_validation['message'], 'score')

            # 检查是否已有成绩记录
            existing_grade = self.model_class.query.filter(
                and_(
                    self.model_class.student_id == grade_data['student_id'],
                    self.model_class.course_id == grade_data['course_id']
                )
            ).first()

            if existing_grade:
                # 更新现有成绩
                existing_grade.score = score_validation['value']
                existing_grade.grade_letter = self._calculate_grade_letter(
                    score_validation['value'], course.passing_grade or 60
                )
                existing_grade.gpa = self._calculate_gpa(existing_grade.grade_letter)
                existing_grade.semester = grade_data.get('semester', course.semester)
                existing_grade.comments = grade_data.get('comments', '')
                existing_grade.updated_at = datetime.utcnow()

                grade = existing_grade
            else:
                # 创建新成绩记录
                grade = self.model_class()
                grade.student_id = grade_data['student_id']
                grade.course_id = grade_data['course_id']
                grade.score = score_validation['value']
                grade.grade_letter = self._calculate_grade_letter(
                    score_validation['value'], course.passing_grade or 60
                )
                grade.gpa = self._calculate_gpa(grade.grade_letter)
                grade.semester = grade_data.get('semester', course.semester)
                grade.comments = grade_data.get('comments', '')
                grade.created_at = datetime.utcnow()

                db.session.add(grade)

            db.session.commit()

            self._log_business_action('grade_created' if existing_grade is None else 'grade_updated', {
                'grade_id': grade.id,
                'student_id': student.id,
                'student_name': student.name,
                'course_id': course.id,
                'course_name': course.name,
                'score': grade.score,
                'grade_letter': grade.grade_letter,
                'gpa': grade.gpa
            })

            return grade.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"创建成绩记录失败: {str(e)}", grade_data=grade_data)
            raise ServiceError("成绩创建服务异常", 'GRADE_CREATE_ERROR')

    def bulk_create_grades(self, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量创建成绩

        Args:
            grades_data: 成绩数据列表

        Returns:
            Dict[str, Any]: 批量处理结果

        Raises:
            ServiceError: 批量处理失败
        """
        try:
            self._check_permission('grade_management')

            processed_count = 0
            failed_count = 0
            errors = []

            for i, grade_data in enumerate(grades_data):
                try:
                    self.create_grade(grade_data)
                    processed_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第 {i+1} 行: {str(e)}")

            result = {
                'total_count': len(grades_data),
                'processed_count': processed_count,
                'failed_count': failed_count,
                'success': failed_count == 0,
                'errors': errors
            }

            self._log_business_action('bulk_grades_created', {
                'total_count': len(grades_data),
                'processed_count': processed_count,
                'failed_count': failed_count
            })

            return result

        except Exception as e:
            self.logger.error(f"批量创建成绩失败: {str(e)}")
            raise ServiceError("批量成绩创建服务异常", 'BULK_GRADE_ERROR')

    # ========================================
    # 成绩查询
    # ========================================

    @cache_result(timeout=300)  # 5分钟缓存
    def get_student_grades(
        self,
        student_id: int,
        semester: str = None,
        course_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        获取学生成绩列表

        Args:
            student_id: 学生ID
            semester: 学期筛选
            course_id: 课程ID筛选

        Returns:
            List[Dict[str, Any]]: 成绩列表
        """
        try:
            # 检查权限
            student = self.student_service.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('grade_management')

            # 构建查询
            query = db.session.query(Grade, Course).join(
                Course, Grade.course_id == Course.id
            ).filter(Grade.student_id == student_id)

            if semester:
                query = query.filter(Grade.semester == semester)
            if course_id:
                query = query.filter(Grade.course_id == course_id)

            query = query.order_by(Grade.semester.desc(), Course.name)

            results = query.all()

            grades = []
            for grade, course in results:
                grade_data = {
                    'grade_id': grade.id,
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'semester': grade.semester,
                    'score': grade.score,
                    'grade_letter': grade.grade_letter,
                    'gpa': grade.gpa,
                    'comments': grade.comments,
                    'graded_at': grade.created_at.isoformat() if grade.created_at else None
                }
                grades.append(grade_data)

            return grades

        except Exception as e:
            self.logger.error(f"获取学生成绩失败: {str(e)}", student_id=student_id)
            raise ServiceError("学生成绩查询服务异常", 'STUDENT_GRADES_ERROR')

    def get_course_grades(self, course_id: int, semester: str = None) -> Dict[str, Any]:
        """
        获取课程成绩统计

        Args:
            course_id: 课程ID
            semester: 学期筛选

        Returns:
            Dict[str, Any]: 成绩统计信息

        Raises:
            ServiceError: 查询失败
        """
        try:
            # 检查权限
            course = self.course_service.get_by_id(course_id)
            if not course:
                raise NotFoundError("课程")

            current_user_id = self._get_current_user_id()
            if course.teacher_id != current_user_id:
                self._check_permission('grade_management')

            # 构建查询
            query = db.session.query(Grade, Student).join(
                Student, Grade.student_id == Student.id
            ).filter(Grade.course_id == course_id)

            if semester:
                query = query.filter(Grade.semester == semester)

            query = query.order_by(Student.name)

            results = query.all()

            grades = []
            total_students = len(results)
            total_score = 0
            grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            passed_count = 0

            for grade, student in results:
                grade_data = {
                    'grade_id': grade.id,
                    'student_id': student.id,
                    'student_number': student.student_id,
                    'student_name': student.name,
                    'grade_level': student.grade_level,
                    'score': grade.score,
                    'grade_letter': grade.grade_letter,
                    'gpa': grade.gpa,
                    'comments': grade.comments,
                    'graded_at': grade.created_at.isoformat() if grade.created_at else None
                }
                grades.append(grade_data)

                # 统计计算
                if grade.score is not None:
                    total_score += grade.score
                    if grade.grade_letter in grade_distribution:
                        grade_distribution[grade.grade_letter] += 1
                    if grade.score >= (course.passing_grade or 60):
                        passed_count += 1

            # 计算统计数据
            average_score = round(total_score / total_students, 2) if total_students > 0 else 0
            pass_rate = round(passed_count / total_students * 100, 2) if total_students > 0 else 0

            return {
                'course_info': course.to_dict(),
                'semester': semester,
                'statistics': {
                    'total_students': total_students,
                    'average_score': average_score,
                    'pass_rate': pass_rate,
                    'grade_distribution': grade_distribution
                },
                'grades': grades
            }

        except Exception as e:
            self.logger.error(f"获取课程成绩失败: {str(e)}", course_id=course_id)
            raise ServiceError("课程成绩查询服务异常", 'COURSE_GRADES_ERROR')

    # ========================================
    # 成绩分析
    # ========================================

    def get_student_gpa(self, student_id: int, semester: str = None) -> Dict[str, Any]:
        """
        获取学生GPA计算

        Args:
            student_id: 学生ID
            semester: 学期筛选

        Returns:
            Dict[str, Any]: GPA信息
        """
        try:
            # 检查权限
            student = self.student_service.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('grade_management')

            # 构建查询
            query = db.session.query(
                func.avg(Grade.gpa).label('avg_gpa'),
                func.sum(Course.credits).label('total_credits'),
                func.count(Grade.id).label('total_courses')
            ).join(Course, Grade.course_id == Course.id)\
             .filter(Grade.student_id == student_id)\
             .filter(Grade.gpa.isnot(None))

            if semester:
                query = query.filter(Grade.semester == semester)

            result = query.first()

            return {
                'student_id': student_id,
                'semester': semester,
                'average_gpa': round(float(result.avg_gpa), 2) if result.avg_gpa else 0,
                'total_credits': int(result.total_credits) if result.total_credits else 0,
                'total_courses': result.total_courses or 0
            }

        except Exception as e:
            self.logger.error(f"获取学生GPA失败: {str(e)}", student_id=student_id)
            raise ServiceError("GPA计算服务异常", 'GPA_CALCULATION_ERROR')

    def get_grade_statistics(self, semester: str = None, department: str = None) -> Dict[str, Any]:
        """
        获取成绩统计信息

        Args:
            semester: 学期筛选
            department: 院系筛选

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 基础查询
            query = db.session.query(Grade, Course, Student).join(
                Course, Grade.course_id == Course.id
            ).join(Student, Grade.student_id == Student.id)

            if semester:
                query = query.filter(Grade.semester == semester)

            # 通过院系筛选
            if department:
                query = query.filter(Student.department == department)

            # 总成绩数
            total_grades = query.count()

            # 按等级分布统计
            grade_distribution = db.session.query(
                Grade.grade_letter,
                func.count(Grade.id)
            ).join(Course, Grade.course_id == Course.id)\
             .join(Student, Grade.student_id == Student.id)\
             .filter_by(**{
                 'semester': semester if semester else Grade.semester
             }).group_by(Grade.grade_letter).all()

            # 平均分统计
            score_stats = db.session.query(
                func.avg(Grade.score).label('avg_score'),
                func.min(Grade.score).label('min_score'),
                func.max(Grade.score).label('max_score'),
                func.count(Grade.id).label('total_count')
            ).filter(Grade.score.isnot(None))

            if semester:
                score_stats = score_stats.join(Course, Grade.course_id == Course.id)\
                                 .join(Student, Grade.student_id == Student.id)\
                                 .filter(Course.semester == semester)

            score_result = score_stats.first()

            # GPA统计
            gpa_stats = db.session.query(
                func.avg(Grade.gpa).label('avg_gpa'),
                func.count(Grade.id).label('total_count')
            ).filter(Grade.gpa.isnot(None))

            if semester:
                gpa_stats = gpa_stats.join(Course, Grade.course_id == Course.id)\
                                .join(Student, Grade.student_id == Student.id)\
                                .filter(Course.semester == semester)

            gpa_result = gpa_stats.first()

            return {
                'total_grades': total_grades,
                'score_statistics': {
                    'average_score': round(float(score_result.avg_score), 2) if score_result.avg_score else 0,
                    'min_score': score_result.min_score,
                    'max_score': score_result.max_score,
                    'count': score_result.total_count or 0
                },
                'gpa_statistics': {
                    'average_gpa': round(float(gpa_result.avg_gpa), 2) if gpa_result.avg_gpa else 0,
                    'count': gpa_result.total_count or 0
                },
                'grade_distribution': {
                    grade: count for grade, count in grade_distribution if grade
                }
            }

        except Exception as e:
            self.logger.error(f"获取成绩统计失败: {str(e)}")
            raise ServiceError("成绩统计服务异常", 'GRADE_STATISTICS_ERROR')

    # ========================================
    # 辅助方法
    # ========================================

    def _calculate_grade_letter(self, score: float, passing_grade: float = 60) -> str:
        """
        计算等级成绩

        Args:
            score: 分数
            passing_grade: 及格分数

        Returns:
            str: 等级成绩 (A, B, C, D, F)
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= passing_grade:
            return 'D'
        else:
            return 'F'

    def _calculate_gpa(self, grade_letter: str) -> float:
        """
        计算GPA

        Args:
            grade_letter: 等级成绩

        Returns:
            float: GPA值
        """
        gpa_mapping = {
            'A': 4.0,
            'B': 3.0,
            'C': 2.0,
            'D': 1.0,
            'F': 0.0
        }

        return gpa_mapping.get(grade_letter, 0.0)

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证成绩数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'student_id' in data:
                student = self.student_service.get_by_id(data['student_id'])
                if not student:
                    raise ValidationError("学生不存在", 'student_id')

            if 'course_id' in data:
                course = self.course_service.get_by_id(data['course_id'])
                if not course:
                    raise ValidationError("课程不存在", 'course_id')

                # 检查选课记录
                enrollment = db.session.query(Enrollment).filter(
                    and_(
                        Enrollment.student_id == data['student_id'],
                        Enrollment.course_id == data['course_id'],
                        Enrollment.status == 'approved'
                    )
                ).first()

                if not enrollment:
                    raise ValidationError("学生未选课或选课未批准", 'no_valid_enrollment')