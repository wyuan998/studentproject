# ========================================
# 学生信息管理系统 - 学生服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, func

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from .user_service import UserService
from ..models import Student, User, UserProfile, Course, Enrollment, Grade, db
from ..utils.validators import PersonalInfoValidator, AcademicValidator
from ..utils.logger import get_structured_logger
from ..utils.cache import cache_result


class StudentService(BaseService):
    """学生服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Student
        self.user_service = UserService()

    # ========================================
    # 学生档案管理
    # ========================================

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建学生档案

        Args:
            student_data: 学生数据

        Returns:
            Dict[str, Any]: 创建的学生信息

        Raises:
            ServiceError: 创建失败
        """
        try:
            # 验证必填字段
            required_fields = ['student_id', 'name', 'user_id']
            for field in required_fields:
                if field not in student_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证学号格式
            student_id_validation = AcademicValidator.validate_student_id(student_data['student_id'])
            if not student_id_validation['valid']:
                raise ValidationError(student_id_validation['message'], 'student_id')

            # 验证姓名
            name_validation = PersonalInfoValidator.validate_name(student_data['name'])
            if not name_validation['valid']:
                raise ValidationError(name_validation['message'], 'name')

            # 验证年级
            if 'grade_level' in student_data:
                grade_validation = AcademicValidator.validate_grade_level(student_data['grade_level'])
                if not grade_validation['valid']:
                    raise ValidationError(grade_validation['message'], 'grade_level')

            # 验证身份证号（如果提供）
            if 'id_card' in student_data and student_data['id_card']:
                id_card_validation = PersonalInfoValidator.validate_id_card(student_data['id_card'])
                if not id_card_validation['valid']:
                    raise ValidationError(id_card_validation['message'], 'id_card')

            # 检查学号是否已存在
            if self.get_by_field('student_id', student_data_validation['normalized']):
                raise BusinessRuleError("学号已存在", 'student_id_exists')

            # 验证用户存在且角色为学生
            user = self.user_service.get_by_id(student_data['user_id'])
            if not user:
                raise NotFoundError("用户")

            if user.role.value != 'student':
                raise BusinessRuleError("用户角色不是学生", 'invalid_role')

            # 检查是否已存在学生档案
            existing_student = self.model_class.query.filter_by(user_id=student_data['user_id']).first()
            if existing_student:
                raise BusinessRuleError("用户已存在学生档案", 'student_exists')

            # 创建学生档案
            student = self.model_class()
            student.student_id = student_id_validation['normalized']
            student.name = name_validation['normalized']
            student.user_id = student_data['user_id']

            # 设置可选字段
            optional_fields = [
                'gender', 'birth_date', 'phone', 'email', 'id_card',
                'address', 'department', 'major', 'grade_level', 'class_name',
                'enrollment_date', 'graduation_date', 'status'
            ]

            for field in optional_fields:
                if field in student_data:
                    if field in ['phone', 'email']:
                        # 特殊验证
                        if field == 'phone':
                            phone_validation = PersonalInfoValidator.validate_phone_number(student_data[field])
                            if not phone_validation['valid']:
                                raise ValidationError(phone_validation['message'], field)
                            setattr(student, field, phone_validation['formatted'])
                        elif field == 'email':
                            email_validation = PersonalInfoValidator.validate_email(student_data[field])
                            if not email_validation['valid']:
                                raise ValidationError(email_validation['message'], field)
                            setattr(student, field, email_validation['normalized'])
                    else:
                        setattr(student, field, student_data[field])

            # 设置默认值
            if not student.status:
                student.status = 'enrolled'
            if not student.enrollment_date:
                student.enrollment_date = date.today()

            student.created_at = datetime.utcnow()

            db.session.add(student)
            db.session.commit()

            # 更新用户档案信息
            if user.profile:
                if not user.profile.name and student.name:
                    user.profile.name = student.name
                if not user.profile.phone and student.phone:
                    user.profile.phone = student.phone
                if not user.profile.email and student.email:
                    user.profile.email = student.email
                user.profile.updated_at = datetime.utcnow()
                db.session.commit()

            self._log_business_action('student_created', {
                'student_id': student.id,
                'student_number': student.student_id,
                'name': student.name,
                'user_id': student.user_id
            })

            return student.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"创建学生档案失败: {str(e)}", student_data=student_data)
            raise ServiceError("学生档案创建服务异常", 'STUDENT_CREATE_ERROR')

    @cache_result(timeout=300)  # 5分钟缓存
    def get_student_by_number(self, student_number: str) -> Optional[Dict[str, Any]]:
        """
        根据学号获取学生信息

        Args:
            student_number: 学号

        Returns:
            Optional[Dict[str, Any]]: 学生信息
        """
        try:
            student = self.get_by_field('student_id', student_number)
            if not student:
                return None

            # 获取相关的课程和成绩信息
            student_dict = student.to_dict()

            # 获取当前学期课程数
            from ..utils.datetime_utils import AcademicCalendar
            current_semester = AcademicCalendar.get_current_semester()
            current_year = datetime.now().year

            enrollments_count = db.session.query(func.count(Enrollment.id)).filter(
                and_(
                    Enrollment.student_id == student.id,
                    Enrollment.semester == f"{current_year}-{current_semester}",
                    Enrollment.status == 'approved'
                )
            ).scalar()

            student_dict['current_courses_count'] = enrollments_count or 0

            # 获取GPA
            gpa_result = db.session.query(func.avg(Grade.gpa)).filter(
                and_(
                    Grade.student_id == student.id,
                    Grade.gpa.isnot(None)
                )
            ).first()

            student_dict['gpa'] = round(float(gpa_result[0]), 2) if gpa_result[0] else None

            return student_dict

        except Exception as e:
            self.logger.error(f"获取学生信息失败: {str(e)}", student_number=student_number)
            raise ServiceError("学生信息查询服务异常", 'STUDENT_QUERY_ERROR')

    def update_student(self, student_id: int, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新学生信息

        Args:
            student_id: 学生ID
            student_data: 更新数据

        Returns:
            Dict[str, Any]: 更新后的学生信息

        Raises:
            ServiceError: 更新失败
        """
        try:
            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            # 检查权限（只能修改自己的信息或管理员权限）
            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('student_management')

            # 验证更新数据
            if 'name' in student_data:
                name_validation = PersonalInfoValidator.validate_name(student_data['name'])
                if not name_validation['valid']:
                    raise ValidationError(name_validation['message'], 'name')

            if 'student_id' in student_data:
                student_id_validation = AcademicValidator.validate_student_id(student_data['student_id'])
                if not student_id_validation['valid']:
                    raise ValidationError(student_id_validation['message'], 'student_id')

                # 检查学号唯一性（排除当前学生）
                existing_student = self.get_by_field('student_id', student_id_validation['normalized'])
                if existing_student and existing_student.id != student_id:
                    raise BusinessRuleError("学号已存在", 'student_id_exists')

            # 更新字段
            for field, value in student_data.items():
                if hasattr(student, field) and field not in ['id', 'user_id', 'created_at']:
                    if field in ['phone', 'email']:
                        # 特殊验证
                        if field == 'phone':
                            phone_validation = PersonalInfoValidator.validate_phone_number(value)
                            if not phone_validation['valid']:
                                raise ValidationError(phone_validation['message'], field)
                            setattr(student, field, phone_validation['formatted'])
                        elif field == 'email':
                            email_validation = PersonalInfoValidator.validate_email(value)
                            if not email_validation['valid']:
                                raise ValidationError(email_validation['message'], field)
                            setattr(student, field, email_validation['normalized'])
                    else:
                        setattr(student, field, value)

            student.updated_at = datetime.utcnow()
            db.session.commit()

            # 同步更新用户档案
            user = self.user_service.get_by_id(student.user_id)
            if user and user.profile:
                if 'name' in student_data:
                    user.profile.name = student_data['name']
                if 'phone' in student_data:
                    user.profile.phone = student.phone
                if 'email' in student_data:
                    user.profile.email = student.email
                user.profile.updated_at = datetime.utcnow()
                db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"student:{student.student_id}:*")
            self._clear_cache_pattern(f"user:{student.user_id}:*")

            self._log_business_action('student_updated', {
                'student_id': student.id,
                'student_number': student.student_id,
                'updated_fields': list(student_data.keys())
            })

            return student.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"更新学生信息失败: {str(e)}", student_id=student_id, student_data=student_data)
            raise ServiceError("学生信息更新服务异常", 'STUDENT_UPDATE_ERROR')

    # ========================================
    # 学生状态管理
    # ========================================

    def change_student_status(self, student_id: int, new_status: str, reason: str = None) -> bool:
        """
        更改学生状态

        Args:
            student_id: 学生ID
            new_status: 新状态 (enrolled, suspended, graduated, withdrawn)
            reason: 变更原因

        Returns:
            bool: 是否更改成功

        Raises:
            ServiceError: 更改失败
        """
        try:
            self._check_permission('student_management')

            valid_statuses = ['enrolled', 'suspended', 'graduated', 'withdrawn']
            if new_status not in valid_statuses:
                raise ValidationError(f"无效的状态: {new_status}", 'status')

            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            old_status = student.status
            student.status = new_status
            student.updated_at = datetime.utcnow()

            # 如果状态变更为毕业，设置毕业日期
            if new_status == 'graduated' and not student.graduation_date:
                student.graduation_date = date.today()

            db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"student:{student.student_id}:*")

            self._log_business_action('student_status_changed', {
                'student_id': student_id,
                'student_number': student.student_id,
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"更改学生状态失败: {str(e)}", student_id=student_id, new_status=new_status)
            raise ServiceError("学生状态更改服务异常", 'STUDENT_STATUS_ERROR')

    # ========================================
    # 学生课程管理
    # ========================================

    def get_student_courses(self, student_id: int, semester: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        获取学生课程列表

        Args:
            student_id: 学生ID
            semester: 学期筛选
            status: 状态筛选

        Returns:
            List[Dict[str, Any]]: 课程列表
        """
        try:
            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('student_management')

            # 构建查询
            query = db.session.query(
                Enrollment, Course, Grade
            ).outerjoin(Course, Enrollment.course_id == Course.id)\
             .outer_join(Grade, and_(
                 Grade.student_id == student_id,
                 Grade.course_id == Course.id
             )).filter(Enrollment.student_id == student_id)

            # 应用筛选条件
            if semester:
                query = query.filter(Enrollment.semester == semester)
            if status:
                query = query.filter(Enrollment.status == status)

            # 按学期排序
            query = query.order_by(Enrollment.semester.desc(), Course.name)

            results = query.all()

            courses = []
            for enrollment, course, grade in results:
                course_data = {
                    'enrollment_id': enrollment.id,
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'teacher_name': course.teacher.name if course.teacher else None,
                    'semester': enrollment.semester,
                    'enrollment_status': enrollment.status,
                    'enrollment_date': enrollment.created_at.isoformat() if enrollment.created_at else None,
                    'grade': {
                        'score': grade.score,
                        'grade_letter': grade.grade_letter,
                        'gpa': grade.gpa,
                        'graded_at': grade.created_at.isoformat() if grade.created_at else None
                    } if grade else None
                }
                courses.append(course_data)

            return courses

        except Exception as e:
            self.logger.error(f"获取学生课程失败: {str(e)}", student_id=student_id)
            raise ServiceError("学生课程查询服务异常", 'STUDENT_COURSES_ERROR')

    def get_student_schedule(self, student_id: int, week: int = None) -> List[Dict[str, Any]]:
        """
        获取学生课程表

        Args:
            student_id: 学生ID
            week: 周数（可选）

        Returns:
            List[Dict[str, Any]]: 课程表数据
        """
        try:
            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('student_management')

            # 获取当前学期已批准的选课
            from ..utils.datetime_utils import AcademicCalendar
            current_semester = AcademicCalendar.get_current_semester()
            current_year = datetime.now().year

            query = db.session.query(
                Enrollment, Course
            ).join(Course, Enrollment.course_id == Course.id)\
             .filter(
                 and_(
                     Enrollment.student_id == student_id,
                     Enrollment.semester == f"{current_year}-{current_semester}",
                     Enrollment.status == 'approved'
                 )
             )

            # 如果指定了周数，添加时间过滤（这里需要根据实际的时间表数据结构调整）
            # if week:
            #     query = query.filter(Schedule.week == week)

            results = query.all()

            schedule_data = []
            for enrollment, course in results:
                # 这里应该查询具体的课程时间安排
                # 暂时返回基本信息
                schedule_item = {
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'teacher_name': course.teacher.name if course.teacher else None,
                    'classroom': '待定',  # 需要从时间表数据中获取
                    'time': '待定',       # 需要从时间表数据中获取
                    'week': week
                }
                schedule_data.append(schedule_item)

            return schedule_data

        except Exception as e:
            self.logger.error(f"获取学生课程表失败: {str(e)}", student_id=student_id)
            raise ServiceError("学生课程表查询服务异常", 'STUDENT_SCHEDULE_ERROR')

    # ========================================
    # 学生成绩管理
    # ========================================

    def get_student_grades(self, student_id: int, semester: str = None) -> Dict[str, Any]:
        """
        获取学生成绩信息

        Args:
            student_id: 学生ID
            semester: 学期筛选

        Returns:
            Dict[str, Any]: 成绩信息
        """
        try:
            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('grade_management')

            # 构建查询
            query = db.session.query(
                Grade, Course
            ).join(Course, Grade.course_id == Course.id)\
             .filter(Grade.student_id == student_id)

            if semester:
                query = query.filter(Grade.semester == semester)

            query = query.order_by(Grade.semester.desc(), Course.name)

            results = query.all()

            grades = []
            total_credits = 0
            total_grade_points = 0
            graded_credits = 0

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
                    'graded_at': grade.created_at.isoformat() if grade.created_at else None
                }
                grades.append(grade_data)

                # 计算GPA相关统计
                if grade.gpa and grade.score is not None:
                    total_credits += course.credits
                    graded_credits += course.credits
                    total_grade_points += grade.gpa * course.credits

            # 计算总体GPA
            overall_gpa = round(total_grade_points / graded_credits, 2) if graded_credits > 0 else 0

            return {
                'student_info': student.to_dict(),
                'grades': grades,
                'statistics': {
                    'total_courses': len(grades),
                    'total_credits': total_credits,
                    'graded_credits': graded_credits,
                    'overall_gpa': overall_gpa
                }
            }

        except Exception as e:
            self.logger.error(f"获取学生成绩失败: {str(e)}", student_id=student_id)
            raise ServiceError("学生成绩查询服务异常", 'STUDENT_GRADES_ERROR')

    def calculate_student_gpa(self, student_id: int, semester: str = None) -> float:
        """
        计算学生GPA

        Args:
            student_id: 学生ID
            semester: 学期（可选）

        Returns:
            float: GPA值
        """
        try:
            student = self.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            query = db.session.query(
                func.avg(Grade.gpa),
                func.sum(Course.credits)
            ).join(Course, Grade.course_id == Course.id)\
             .filter(
                 and_(
                     Grade.student_id == student_id,
                     Grade.gpa.isnot(None),
                     Grade.score.isnot(None)
                 )
             )

            if semester:
                query = query.filter(Grade.semester == semester)

            result = query.first()
            avg_gpa = result[0] if result[0] else 0

            return round(float(avg_gpa), 2)

        except Exception as e:
            self.logger.error(f"计算学生GPA失败: {str(e)}", student_id=student_id)
            raise ServiceError("GPA计算服务异常", 'GPA_CALCULATION_ERROR')

    # ========================================
    # 学生统计和分析
    # ========================================

    def get_student_statistics(self, department: str = None, grade_level: str = None) -> Dict[str, Any]:
        """
        获取学生统计信息

        Args:
            department: 院系筛选
            grade_level: 年级筛选

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 基础查询
            query = self.model_class.query

            # 应用筛选条件
            if department:
                query = query.filter(self.model_class.department == department)
            if grade_level:
                query = query.filter(self.model_class.grade_level == grade_level)

            # 总数统计
            total_students = query.count()

            # 按状态统计
            status_stats = db.session.query(
                self.model_class.status,
                func.count(self.model_class.id)
            ).filter_by(**{
                'department': department if department else self.model_class.department,
                'grade_level': grade_level if grade_level else self.model_class.grade_level
            }).group_by(self.model_class.status).all()

            # 按年级统计
            grade_stats = db.session.query(
                self.model_class.grade_level,
                func.count(self.model_class.id)
            ).filter_by(**{
                'department': department if department else self.model_class.department
            }).group_by(self.model_class.grade_level).all()

            # 按院系统计
            dept_stats = db.session.query(
                self.model_class.department,
                func.count(self.model_class.id)
            ).filter_by(**{
                'grade_level': grade_level if grade_level else self.model_class.grade_level
            }).group_by(self.model_class.department).all()

            # 本月新增学生
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_students_this_month = query.filter(
                self.model_class.created_at >= current_month_start
            ).count()

            return {
                'total_students': total_students,
                'new_students_this_month': new_students_this_month,
                'status_distribution': {
                    status: count for status, count in status_stats
                },
                'grade_distribution': {
                    grade: count for grade, count in grade_stats if grade
                },
                'department_distribution': {
                    dept: count for dept, count in dept_stats if dept
                }
            }

        except Exception as e:
            self.logger.error(f"获取学生统计失败: {str(e)}")
            raise ServiceError("学生统计服务异常", 'STUDENT_STATISTICS_ERROR')

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证学生数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'student_id' in data:
                student_id_validation = AcademicValidator.validate_student_id(data['student_id'])
                if not student_id_validation['valid']:
                    raise ValidationError(student_id_validation['message'], 'student_id')

                # 检查学号唯一性
                if self.get_by_field('student_id', student_id_validation['normalized']):
                    raise BusinessRuleError("学号已存在", 'student_id_exists')

            if 'user_id' in data:
                # 验证用户存在且角色为学生
                user = self.user_service.get_by_id(data['user_id'])
                if not user:
                    raise ValidationError("用户不存在", 'user_id')

                if user.role.value != 'student':
                    raise ValidationError("用户角色不是学生", 'user_id')

                # 检查是否已存在学生档案
                existing_student = self.model_class.query.filter_by(user_id=data['user_id']).first()
                if existing_student:
                    raise BusinessRuleError("用户已存在学生档案", 'student_exists')

        elif operation == 'update':
            # 更新时的验证
            if 'student_id' in data:
                student_id_validation = AcademicValidator.validate_student_id(data['student_id'])
                if not student_id_validation['valid']:
                    raise ValidationError(student_id_validation['message'], 'student_id')

                # 检查学号唯一性（排除当前学生）
                existing_student = self.get_by_field('student_id', student_id_validation['normalized'])
                if existing_student and existing_student.id != instance.id:
                    raise BusinessRuleError("学号已存在", 'student_id_exists')

            if 'user_id' in data:
                # 验证用户存在且角色为学生
                user = self.user_service.get_by_id(data['user_id'])
                if not user:
                    raise ValidationError("用户不存在", 'user_id')

                if user.role.value != 'student':
                    raise ValidationError("用户角色不是学生", 'user_id')

                # 检查是否已被其他学生使用
                existing_student = self.model_class.query.filter_by(user_id=data['user_id']).first()
                if existing_student and existing_student.id != instance.id:
                    raise BusinessRuleError("用户已被其他学生档案使用", 'user_id_in_use')