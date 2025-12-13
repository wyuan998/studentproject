# ========================================
# 学生信息管理系统 - 教师服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, func

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from .user_service import UserService
from ..models import Teacher, User, UserProfile, Course, Enrollment, Grade, db
from ..utils.validators import PersonalInfoValidator, AcademicValidator
from ..utils.logger import get_structured_logger


class TeacherService(BaseService):
    """教师服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Teacher
        self.user_service = UserService()

    # ========================================
    # 教师档案管理
    # ========================================

    def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建教师档案

        Args:
            teacher_data: 教师数据

        Returns:
            Dict[str, Any]: 创建的教师信息

        Raises:
            ServiceError: 创建失败
        """
        try:
            # 验证必填字段
            required_fields = ['teacher_id', 'name', 'user_id']
            for field in required_fields:
                if field not in teacher_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证姓名
            name_validation = PersonalInfoValidator.validate_name(teacher_data['name'])
            if not name_validation['valid']:
                raise ValidationError(name_validation['message'], 'name')

            # 验证工号
            if 'teacher_id' in teacher_data:
                teacher_id_validation = PersonalInfoValidator.validate_name(
                    teacher_data['teacher_id'],
                    min_length=3,
                    max_length=20
                )
                if not teacher_id_validation['valid']:
                    raise ValidationError("工号格式不正确", 'teacher_id')

                # 检查工号唯一性
                if self.get_by_field('teacher_id', teacher_id_validation['normalized']):
                    raise BusinessRuleError("工号已存在", 'teacher_id_exists')

            # 验证用户存在且角色为教师
            user = self.user_service.get_by_id(teacher_data['user_id'])
            if not user:
                raise NotFoundError("用户")

            if user.role.value != 'teacher':
                raise BusinessRuleError("用户角色不是教师", 'invalid_role')

            # 检查是否已存在教师档案
            existing_teacher = self.model_class.query.filter_by(user_id=teacher_data['user_id']).first()
            if existing_teacher:
                raise BusinessRuleError("用户已存在教师档案", 'teacher_exists')

            # 创建教师档案
            teacher = self.model_class()
            teacher.teacher_id = teacher_data.get('teacher_id', f"T{datetime.now().strftime('%Y%m%d%H%M%S')}")
            teacher.name = name_validation['normalized']
            teacher.user_id = teacher_data['user_id']

            # 设置可选字段
            optional_fields = [
                'gender', 'birth_date', 'phone', 'email', 'id_card',
                'address', 'department', 'title', 'education', 'major',
                'join_date', 'research_direction', 'office', 'workload'
            ]

            for field in optional_fields:
                if field in teacher_data:
                    if field in ['phone', 'email']:
                        # 特殊验证
                        if field == 'phone':
                            phone_validation = PersonalInfoValidator.validate_phone_number(teacher_data[field])
                            if not phone_validation['valid']:
                                raise ValidationError(phone_validation['message'], field)
                            setattr(teacher, field, phone_validation['formatted'])
                        elif field == 'email':
                            email_validation = PersonalInfoValidator.validate_email(teacher_data[field])
                            if not email_validation['valid']:
                                raise ValidationError(email_validation['message'], field)
                            setattr(teacher, field, email_validation['normalized'])
                    else:
                        setattr(teacher, field, teacher_data[field])

            # 设置默认值
            if not teacher.join_date:
                teacher.join_date = date.today()
            if not teacher.workload:
                teacher.workload = 0
            if not teacher.status:
                teacher.status = 'active'

            teacher.created_at = datetime.utcnow()

            db.session.add(teacher)
            db.session.commit()

            # 更新用户档案信息
            if user.profile:
                if not user.profile.name and teacher.name:
                    user.profile.name = teacher.name
                if not user.profile.phone and teacher.phone:
                    user.profile.phone = teacher.phone
                if not user.profile.email and teacher.email:
                    user.profile.email = teacher.email
                user.profile.updated_at = datetime.utcnow()
                db.session.commit()

            self._log_business_action('teacher_created', {
                'teacher_id': teacher.id,
                'teacher_number': teacher.teacher_id,
                'name': teacher.name,
                'user_id': teacher.user_id
            })

            return teacher.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"创建教师档案失败: {str(e)}", teacher_data=teacher_data)
            raise ServiceError("教师档案创建服务异常", 'TEACHER_CREATE_ERROR')

    def get_teacher_by_number(self, teacher_number: str) -> Optional[Dict[str, Any]]:
        """
        根据工号获取教师信息

        Args:
            teacher_number: 工号

        Returns:
            Optional[Dict[str, Any]]: 教师信息
        """
        try:
            teacher = self.get_by_field('teacher_id', teacher_number)
            if not teacher:
                return None

            # 获取相关信息
            teacher_dict = teacher.to_dict()

            # 获取当前学期课程数
            from ..utils.datetime_utils import AcademicCalendar
            current_semester = AcademicCalendar.get_current_semester()
            current_year = datetime.now().year

            courses_count = db.session.query(func.count(Course.id)).filter(
                and_(
                    Course.teacher_id == teacher.id,
                    Course.semester == f"{current_year}-{current_semester}"
                )
            ).scalar()

            teacher_dict['current_courses_count'] = courses_count or 0

            # 获取学生总数
            total_students = db.session.query(func.count(Enrollment.id)).filter(
                and_(
                    Course.teacher_id == teacher.id,
                    Enrollment.course_id == Course.id,
                    Enrollment.status == 'approved'
                )
            ).scalar()

            teacher_dict['total_students'] = total_students or 0

            return teacher_dict

        except Exception as e:
            self.logger.error(f"获取教师信息失败: {str(e)}", teacher_number=teacher_number)
            raise ServiceError("教师信息查询服务异常", 'TEACHER_QUERY_ERROR')

    def update_teacher(self, teacher_id: int, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新教师信息

        Args:
            teacher_id: 教师ID
            teacher_data: 更新数据

        Returns:
            Dict[str, Any]: 更新后的教师信息

        Raises:
            ServiceError: 更新失败
        """
        try:
            teacher = self.get_by_id(teacher_id)
            if not teacher:
                raise NotFoundError("教师")

            # 检查权限（只能修改自己的信息或管理员权限）
            current_user_id = self._get_current_user_id()
            if teacher.user_id != current_user_id:
                self._check_permission('teacher_management')

            # 验证更新数据
            if 'name' in teacher_data:
                name_validation = PersonalInfoValidator.validate_name(teacher_data['name'])
                if not name_validation['valid']:
                    raise ValidationError(name_validation['message'], 'name')

            if 'teacher_id' in teacher_data:
                # 验证工号格式
                teacher_id_validation = PersonalInfoValidator.validate_name(
                    teacher_data['teacher_id'],
                    min_length=3,
                    max_length=20
                )
                if not teacher_id_validation['valid']:
                    raise ValidationError("工号格式不正确", 'teacher_id')

                # 检查工号唯一性（排除当前教师）
                existing_teacher = self.get_by_field('teacher_id', teacher_id_validation['normalized'])
                if existing_teacher and existing_teacher.id != teacher_id:
                    raise BusinessRuleError("工号已存在", 'teacher_id_exists')

            # 更新字段
            for field, value in teacher_data.items():
                if hasattr(teacher, field) and field not in ['id', 'user_id', 'created_at']:
                    if field in ['phone', 'email']:
                        # 特殊验证
                        if field == 'phone':
                            phone_validation = PersonalInfoValidator.validate_phone_number(value)
                            if not phone_validation['valid']:
                                raise ValidationError(phone_validation['message'], field)
                            setattr(teacher, field, phone_validation['formatted'])
                        elif field == 'email':
                            email_validation = PersonalInfoValidator.validate_email(value)
                            if not email_validation['valid']:
                                raise ValidationError(email_validation['message'], field)
                            setattr(teacher, field, email_validation['normalized'])
                    else:
                        setattr(teacher, field, value)

            teacher.updated_at = datetime.utcnow()
            db.session.commit()

            # 同步更新用户档案
            user = self.user_service.get_by_id(teacher.user_id)
            if user and user.profile:
                if 'name' in teacher_data:
                    user.profile.name = teacher_data['name']
                if 'phone' in teacher_data:
                    user.profile.phone = teacher.phone
                if 'email' in teacher_data:
                    user.profile.email = teacher.email
                user.profile.updated_at = datetime.utcnow()
                db.session.commit()

            self._log_business_action('teacher_updated', {
                'teacher_id': teacher.id,
                'teacher_number': teacher.teacher_id,
                'updated_fields': list(teacher_data.keys())
            })

            return teacher.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"更新教师信息失败: {str(e)}", teacher_id=teacher_id, teacher_data=teacher_data)
            raise ServiceError("教师信息更新服务异常", 'TEACHER_UPDATE_ERROR')

    # ========================================
    # 教师课程管理
    # ========================================

    def get_teacher_courses(self, teacher_id: int, semester: str = None) -> List[Dict[str, Any]]:
        """
        获取教师课程列表

        Args:
            teacher_id: 教师ID
            semester: 学期筛选

        Returns:
            List[Dict[str, Any]]: 课程列表
        """
        try:
            teacher = self.get_by_id(teacher_id)
            if not teacher:
                raise NotFoundError("教师")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if teacher.user_id != current_user_id:
                self._check_permission('course_management')

            # 构建查询
            query = Course.query.filter(Course.teacher_id == teacher_id)

            if semester:
                query = query.filter(Course.semester == semester)

            query = query.order_by(Course.semester.desc(), Course.name)
            courses = query.all()

            # 获取每个课程的选课人数
            course_list = []
            for course in courses:
                enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.status == 'approved'
                    )
                ).scalar()

                course_data = {
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'credits': course.credits,
                    'capacity': course.capacity,
                    'enrolled_students': enrollment_count or 0,
                    'category': course.category,
                    'semester': course.semester,
                    'status': course.status,
                    'created_at': course.created_at.isoformat() if course.created_at else None
                }
                course_list.append(course_data)

            return course_list

        except Exception as e:
            self.logger.error(f"获取教师课程失败: {str(e)}", teacher_id=teacher_id)
            raise ServiceError("教师课程查询服务异常", 'TEACHER_COURSES_ERROR')

    def get_teacher_students(self, teacher_id: int, course_id: int = None) -> List[Dict[str, Any]]:
        """
        获取教师的学生列表

        Args:
            teacher_id: 教师ID
            course_id: 课程ID（可选）

        Returns:
            List[Dict[str, Any]]: 学生列表
        """
        try:
            teacher = self.get_by_id(teacher_id)
            if not teacher:
                raise NotFoundError("教师")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if teacher.user_id != current_user_id:
                self._check_permission('student_management')

            # 构建查询
            query = db.session.query(
                Enrollment, Student, Course, Grade
            ).join(Student, Enrollment.student_id == Student.id)\
             .join(Course, Enrollment.course_id == Course.id)\
             .outer_join(Grade, and_(
                 Grade.student_id == Student.id,
                 Grade.course_id == Course.id
             )).filter(
                 and_(
                     Course.teacher_id == teacher_id,
                     Enrollment.status == 'approved'
                 )
             )

            if course_id:
                query = query.filter(Course.id == course_id)

            query = query.order_by(Course.name, Student.name)

            results = query.all()

            students = []
            for enrollment, student, course, grade in results:
                student_data = {
                    'student_id': student.id,
                    'student_number': student.student_id,
                    'name': student.name,
                    'grade_level': student.grade_level,
                    'department': student.department,
                    'major': student.major,
                    'enrollment_id': enrollment.id,
                    'course_id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.name,
                    'semester': enrollment.semester,
                    'enrollment_date': enrollment.created_at.isoformat() if enrollment.created_at else None,
                    'grade': {
                        'score': grade.score,
                        'grade_letter': grade.grade_letter,
                        'gpa': grade.gpa,
                        'graded_at': grade.created_at.isoformat() if grade.created_at else None
                    } if grade else None
                }
                students.append(student_data)

            return students

        except Exception as e:
            self.logger.error(f"获取教师学生列表失败: {str(e)}", teacher_id=teacher_id)
            raise ServiceError("教师学生查询服务异常", 'TEACHER_STUDENTS_ERROR')

    # ========================================
    # 教师工作统计
    # ========================================

    def get_teacher_workload(self, teacher_id: int, semester: str = None) -> Dict[str, Any]:
        """
        获取教师工作量统计

        Args:
            teacher_id: 教师ID
            semester: 学期筛选

        Returns:
            Dict[str, Any]: 工作量统计
        """
        try:
            teacher = self.get_by_id(teacher_id)
            if not teacher:
                raise NotFoundError("教师")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if teacher.user_id != current_user_id:
                self._check_permission('teacher_management')

            # 构建查询
            query = Course.query.filter(Course.teacher_id == teacher_id)

            if semester:
                query = query.filter(Course.semester == semester)

            courses = query.all()

            # 统计工作量
            total_courses = len(courses)
            total_students = 0
            total_credits = 0
            course_details = []

            for course in courses:
                enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.status == 'approved'
                    )
                ).scalar() or 0

                # 计算工作量（基础工作量 + 学生数权重）
                base_workload = 1.0  # 每门课程基础工作量
                student_workload = min(enrollment_count / 30, 2.0)  # 学生数权重，最多2.0
                course_workload = base_workload + student_workload

                total_students += enrollment_count
                total_credits += course.credits or 0

                course_details.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'credits': course.credits or 0,
                    'students_count': enrollment_count,
                    'workload': course_workload
                })

            # 总工作量
            total_workload = sum(course['workload'] for course in course_details)

            return {
                'teacher_info': teacher.to_dict(),
                'semester': semester,
                'statistics': {
                    'total_courses': total_courses,
                    'total_students': total_students,
                    'total_credits': total_credits,
                    'total_workload': round(total_workload, 2),
                    'average_students_per_course': round(total_students / total_courses, 2) if total_courses > 0 else 0
                },
                'course_details': course_details
            }

        except Exception as e:
            self.logger.error(f"获取教师工作量统计失败: {str(e)}", teacher_id=teacher_id)
            raise ServiceError("教师工作量统计服务异常", 'TEACHER_WORKLOAD_ERROR')

    # ========================================
    # 教师统计分析
    # ========================================

    def get_teacher_statistics(self, department: str = None, title: str = None) -> Dict[str, Any]:
        """
        获取教师统计信息

        Args:
            department: 院系筛选
            title: 职称筛选

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 基础查询
            query = self.model_class.query

            # 应用筛选条件
            if department:
                query = query.filter(self.model_class.department == department)
            if title:
                query = query.filter(self.model_class.title == title)

            # 总数统计
            total_teachers = query.count()

            # 按职称统计
            title_stats = db.session.query(
                self.model_class.title,
                func.count(self.model_class.id)
            ).filter_by(**{
                'department': department if department else self.model_class.department
            }).group_by(self.model_class.title).all()

            # 按院系统计
            dept_stats = db.session.query(
                self.model_class.department,
                func.count(self.model_class.id)
            ).filter_by(**{
                'title': title if title else self.model_class.title
            }).group_by(self.model_class.department).all()

            # 按学历统计
            education_stats = db.session.query(
                self.model_class.education,
                func.count(self.model_class.id)
            ).filter_by(**{
                'department': department if department else self.model_class.department,
                'title': title if title else self.model_class.title
            }).group_by(self.model_class.education).all()

            # 平均工作量
            avg_workload = db.session.query(func.avg(self.model_class.workload)).filter(
                self.model_class.workload.isnot(None)
            ).scalar()

            # 本月新增教师
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_teachers_this_month = query.filter(
                self.model_class.created_at >= current_month_start
            ).count()

            return {
                'total_teachers': total_teachers,
                'new_teachers_this_month': new_teachers_this_month,
                'average_workload': round(float(avg_workload), 2) if avg_workload else 0,
                'title_distribution': {
                    title_val: count for title_val, count in title_stats if title_val
                },
                'department_distribution': {
                    dept: count for dept, count in dept_stats if dept
                },
                'education_distribution': {
                    edu: count for edu, count in education_stats if edu
                }
            }

        except Exception as e:
            self.logger.error(f"获取教师统计失败: {str(e)}")
            raise ServiceError("教师统计服务异常", 'TEACHER_STATISTICS_ERROR')

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证教师数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'teacher_id' in data:
                teacher_id_validation = PersonalInfoValidator.validate_name(
                    data['teacher_id'],
                    min_length=3,
                    max_length=20
                )
                if not teacher_id_validation['valid']:
                    raise ValidationError("工号格式不正确", 'teacher_id')

                # 检查工号唯一性
                if self.get_by_field('teacher_id', teacher_id_validation['normalized']):
                    raise BusinessRuleError("工号已存在", 'teacher_id_exists')

            if 'user_id' in data:
                # 验证用户存在且角色为教师
                user = self.user_service.get_by_id(data['user_id'])
                if not user:
                    raise ValidationError("用户不存在", 'user_id')

                if user.role.value != 'teacher':
                    raise ValidationError("用户角色不是教师", 'user_id')

                # 检查是否已存在教师档案
                existing_teacher = self.model_class.query.filter_by(user_id=data['user_id']).first()
                if existing_teacher:
                    raise BusinessRuleError("用户已存在教师档案", 'teacher_exists')

        elif operation == 'update':
            # 更新时的验证
            if 'teacher_id' in data:
                teacher_id_validation = PersonalInfoValidator.validate_name(
                    data['teacher_id'],
                    min_length=3,
                    max_length=20
                )
                if not teacher_id_validation['valid']:
                    raise ValidationError("工号格式不正确", 'teacher_id')

                # 检查工号唯一性（排除当前教师）
                existing_teacher = self.get_by_field('teacher_id', teacher_id_validation['normalized'])
                if existing_teacher and existing_teacher.id != instance.id:
                    raise BusinessRuleError("工号已存在", 'teacher_id_exists')

            if 'user_id' in data:
                # 验证用户存在且角色为教师
                user = self.user_service.get_by_id(data['user_id'])
                if not user:
                    raise ValidationError("用户不存在", 'user_id')

                if user.role.value != 'teacher':
                    raise ValidationError("用户角色不是教师", 'user_id')

                # 检查是否已被其他教师使用
                existing_teacher = self.model_class.query.filter_by(user_id=data['user_id']).first()
                if existing_teacher and existing_teacher.id != instance.id:
                    raise BusinessRuleError("用户已被其他教师档案使用", 'user_id_in_use')