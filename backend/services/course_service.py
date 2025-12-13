# ========================================
# 学生信息管理系统 - 课程服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, func

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from .teacher_service import TeacherService
from ..models import Course, Teacher, Enrollment, Grade, db
from ..utils.validators import AcademicValidator
from ..utils.logger import get_structured_logger
from ..utils.cache import cache_result


class CourseService(BaseService):
    """课程服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Course
        self.teacher_service = TeacherService()

    # ========================================
    # 课程管理
    # ========================================

    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建课程

        Args:
            course_data: 课程数据

        Returns:
            Dict[str, Any]: 创建的课程信息

        Raises:
            ServiceError: 创建失败
        """
        try:
            # 验证必填字段
            required_fields = ['course_code', 'name', 'credits', 'semester', 'teacher_id']
            for field in required_fields:
                if field not in course_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证课程代码
            if 'course_code' in course_data:
                course_code_validation = AcademicValidator.validate_course_code(course_data['course_code'])
                if not course_code_validation['valid']:
                    raise ValidationError(course_code_validation['message'], 'course_code')

                # 检查课程代码唯一性
                if self.get_by_field('course_code', course_code_validation['normalized']):
                    raise BusinessRuleError("课程代码已存在", 'course_code_exists')

            # 验证学分
            if 'credits' in course_data:
                credits_validation = AcademicValidator.validate_credits(course_data['credits'])
                if not credits_validation['valid']:
                    raise ValidationError(credits_validation['message'], 'credits')

            # 验证学期
            if 'semester' in course_data:
                semester_validation = AcademicValidator.validate_semester(course_data['semester'])
                if not semester_validation['valid']:
                    raise ValidationError(semester_validation['message'], 'semester')

            # 验证教师存在
            if 'teacher_id' in course_data:
                teacher = self.teacher_service.get_by_id(course_data['teacher_id'])
                if not teacher:
                    raise ValidationError("教师不存在", 'teacher_id')

            # 创建课程
            course = self.model_class()
            course.course_code = course_code_validation['normalized']
            course.name = course_data['name']
            course.credits = credits_validation['value'] if 'credits' in course_data else 0
            course.semester = course_data['semester']
            course.teacher_id = course_data['teacher_id']

            # 设置可选字段
            optional_fields = [
                'description', 'category', 'capacity', 'location',
                'schedule', 'prerequisites', 'objectives', 'assessment',
                'textbook', 'status'
            ]

            for field in optional_fields:
                if field in course_data:
                    setattr(course, field, course_data[field])

            # 设置默认值
            if not course.capacity:
                course.capacity = 100
            if not course.status:
                course.status = 'active'
            if not course.category:
                course.category = 'general'

            course.created_at = datetime.utcnow()

            db.session.add(course)
            db.session.commit()

            self._log_business_action('course_created', {
                'course_id': course.id,
                'course_code': course.course_code,
                'course_name': course.name,
                'teacher_id': course.teacher_id,
                'credits': course.credits,
                'semester': course.semester
            })

            return course.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"创建课程失败: {str(e)}", course_data=course_data)
            raise ServiceError("课程创建服务异常", 'COURSE_CREATE_ERROR')

    @cache_result(timeout=600)  # 10分钟缓存
    def get_course_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        根据课程代码获取课程信息

        Args:
            course_code: 课程代码

        Returns:
            Optional[Dict[str, Any]]: 课程信息
        """
        try:
            course = self.get_by_field('course_code', course_code)
            if not course:
                return None

            # 获取扩展信息
            course_dict = course.to_dict()

            # 获取教师信息
            if course.teacher:
                course_dict['teacher'] = {
                    'id': course.teacher.id,
                    'name': course.teacher.name,
                    'title': course.teacher.title,
                    'department': course.teacher.department
                }

            # 获取选课人数
            enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                and_(
                    Enrollment.course_id == course.id,
                    Enrollment.status == 'approved'
                )
            ).scalar()

            course_dict['enrolled_count'] = enrollment_count or 0
            course_dict['available_spots'] = max(0, course.capacity - (enrollment_count or 0))

            # 获取平均成绩
            avg_grade = db.session.query(func.avg(Grade.score)).filter(
                and_(
                    Grade.course_id == course.id,
                    Grade.score.isnot(None)
                )
            ).first()

            course_dict['average_score'] = round(float(avg_grade[0]), 2) if avg_grade[0] else None

            return course_dict

        except Exception as e:
            self.logger.error(f"获取课程信息失败: {str(e)}", course_code=course_code)
            raise ServiceError("课程信息查询服务异常", 'COURSE_QUERY_ERROR')

    def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新课程信息

        Args:
            course_id: 课程ID
            course_data: 更新数据

        Returns:
            Dict[str, Any]: 更新后的课程信息

        Raises:
            ServiceError: 更新失败
        """
        try:
            course = self.get_by_id(course_id)
            if not course:
                raise NotFoundError("课程")

            # 检查权限（课程教师或管理员）
            current_user_id = self._get_current_user_id()
            if course.teacher_id != current_user_id:
                self._check_permission('course_management')

            # 验证更新数据
            if 'course_code' in course_data:
                course_code_validation = AcademicValidator.validate_course_code(course_data['course_code'])
                if not course_code_validation['valid']:
                    raise ValidationError(course_code_validation['message'], 'course_code')

                # 检查课程代码唯一性（排除当前课程）
                existing_course = self.get_by_field('course_code', course_code_validation['normalized'])
                if existing_course and existing_course.id != course_id:
                    raise BusinessRuleError("课程代码已存在", 'course_code_exists')

            if 'credits' in course_data:
                credits_validation = AcademicValidator.validate_credits(course_data['credits'])
                if not credits_validation['valid']:
                    raise ValidationError(credits_validation['message'], 'credits')

            if 'teacher_id' in course_data:
                teacher = self.teacher_service.get_by_id(course_data['teacher_id'])
                if not teacher:
                    raise ValidationError("教师不存在", 'teacher_id')

            # 业务规则：课程已有选课学生时，不能修改某些关键信息
            enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                and_(
                    Enrollment.course_id == course_id,
                    Enrollment.status == 'approved'
                )
            ).scalar()

            restricted_fields = ['credits', 'semester', 'category']
            for field in restricted_fields:
                if field in course_data and enrollment_count > 0:
                    self._check_permission('course_management')  # 只有管理员可以修改

            # 更新字段
            for field, value in course_data.items():
                if hasattr(course, field) and field not in ['id', 'created_at']:
                    setattr(course, field, value)

            course.updated_at = datetime.utcnow()
            db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"course:{course.course_code}:*")

            self._log_business_action('course_updated', {
                'course_id': course.id,
                'course_code': course.course_code,
                'updated_fields': list(course_data.keys())
            })

            return course.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"更新课程信息失败: {str(e)}", course_id=course_id, course_data=course_data)
            raise ServiceError("课程更新服务异常", 'COURSE_UPDATE_ERROR')

    def delete_course(self, course_id: int, soft_delete: bool = True) -> bool:
        """
        删除课程

        Args:
            course_id: 课程ID
            soft_delete: 是否软删除

        Returns:
            bool: 是否删除成功

        Raises:
            ServiceError: 删除失败
        """
        try:
            course = self.get_by_id(course_id)
            if not course:
                raise NotFoundError("课程")

            # 检查权限
            current_user_id = self._get_current_user_id()
            if course.teacher_id != current_user_id:
                self._check_permission('course_management')

            # 检查是否有选课学生
            enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                Enrollment.course_id == course_id
            ).scalar()

            if enrollment_count > 0:
                if soft_delete:
                    # 软删除：将状态设为inactive
                    course.status = 'inactive'
                    course.updated_at = datetime.utcnow()
                    db.session.commit()

                    self._log_business_action('course_soft_deleted', {
                        'course_id': course.id,
                        'course_code': course.course_code,
                        'enrollment_count': enrollment_count
                    })

                    return True
                else:
                    # 硬删除：需要先删除相关选课记录
                    raise BusinessRuleError("课程有选课学生，无法删除", 'course_has_enrollments')

            # 没有选课学生，可以直接删除
            if soft_delete:
                course.status = 'inactive'
                course.updated_at = datetime.utcnow()
                db.session.commit()
            else:
                db.session.delete(course)
                db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"course:{course.course_code}:*")

            self._log_business_action('course_deleted', {
                'course_id': course.id,
                'course_code': course.course_code,
                'soft_delete': soft_delete
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"删除课程失败: {str(e)}", course_id=course_id)
            raise ServiceError("课程删除服务异常", 'COURSE_DELETE_ERROR')

    # ========================================
    # 课程查询
    # ========================================

    def get_courses_list(
        self,
        teacher_id: int = None,
        semester: str = None,
        category: str = None,
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取课程列表

        Args:
            teacher_id: 教师ID筛选
            semester: 学期筛选
            category: 类别筛选
            status: 状态筛选
            page: 页码
            per_page: 每页数量

        Returns:
            Dict[str, Any]: 课程列表和分页信息
        """
        try:
            filters = {}

            if teacher_id:
                filters['teacher_id'] = teacher_id
            if semester:
                filters['semester'] = semester
            if category:
                filters['category'] = category
            if status:
                filters['status'] = status

            result = self.get_list(
                filters=filters,
                page=page,
                per_page=per_page,
                sort_by='created_at',
                sort_order='desc'
            )

            # 为每个课程添加额外信息
            courses_with_details = []
            for course in result['items']:
                course_dict = course.to_dict()

                # 获取选课人数
                enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.status == 'approved'
                    )
                ).scalar()

                course_dict['enrolled_count'] = enrollment_count or 0
                course_dict['available_spots'] = max(0, course.capacity - (enrollment_count or 0))

                # 获取教师信息
                if course.teacher:
                    course_dict['teacher'] = {
                        'id': course.teacher.id,
                        'name': course.teacher.name,
                        'title': course.teacher.title
                    }

                courses_with_details.append(course_dict)

            result['items'] = courses_with_details
            return result

        except Exception as e:
            self.logger.error(f"获取课程列表失败: {str(e)}")
            raise ServiceError("课程列表查询服务异常", 'COURSE_LIST_ERROR')

    def search_courses(self, keyword: str, filters: Dict = None) -> List[Dict[str, Any]]:
        """
        搜索课程

        Args:
            keyword: 搜索关键词
            filters: 额外筛选条件

        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            # 构建搜索查询
            query = self.model_class.query.filter(
                and_(
                    self.model_class.deleted_at.is_(None),
                    self.model_class.status == 'active',
                    or_(
                        self.model_class.name.like(f'%{keyword}%'),
                        self.model_class.course_code.like(f'%{keyword}%'),
                        self.model_class.description.like(f'%{keyword}%')
                    )
                )
            )

            # 应用额外筛选条件
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.filter(getattr(self.model_class, field) == value)

            query = query.order_by(self.model_class.name)
            courses = query.limit(50).all()  # 限制搜索结果数量

            # 格式化结果
            search_results = []
            for course in courses:
                course_dict = course.to_dict()

                # 获取选课人数
                enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.status == 'approved'
                    )
                ).scalar()

                course_dict['enrolled_count'] = enrollment_count or 0
                course_dict['available_spots'] = max(0, course.capacity - (enrollment_count or 0))

                # 获取教师信息
                if course.teacher:
                    course_dict['teacher'] = {
                        'id': course.teacher.id,
                        'name': course.teacher.name,
                        'title': course.teacher.title,
                        'department': course.teacher.department
                    }

                search_results.append(course_dict)

            return search_results

        except Exception as e:
            self.logger.error(f"搜索课程失败: {str(e)}", keyword=keyword)
            raise ServiceError("课程搜索服务异常", 'COURSE_SEARCH_ERROR')

    # ========================================
    # 课程统计
    # ========================================

    def get_course_statistics(self, semester: str = None, department: str = None) -> Dict[str, Any]:
        """
        获取课程统计信息

        Args:
            semester: 学期筛选
            department: 院系筛选（通过教师）

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 基础查询
            query = self.model_class.query

            if semester:
                query = query.filter(self.model_class.semester == semester)

            # 通过教师院系筛选
            if department:
                query = query.join(Teacher).filter(Teacher.department == department)

            # 总数统计
            total_courses = query.count()

            # 按类别统计
            category_stats = db.session.query(
                self.model_class.category,
                func.count(self.model_class.id)
            ).filter_by(**{
                'semester': semester if semester else self.model_class.semester
            }).group_by(self.model_class.category).all()

            # 按状态统计
            status_stats = db.session.query(
                self.model_class.status,
                func.count(self.model_class.id)
            ).filter_by(**{
                'semester': semester if semester else self.model_class.semester
            }).group_by(self.model_class.status).all()

            # 按学分统计
            credit_stats = db.session.query(
                func.sum(self.model_class.credits).label('total_credits'),
                func.avg(self.model_class.credits).label('avg_credits'),
                func.min(self.model_class.credits).label('min_credits'),
                func.max(self.model_class.credits).label('max_credits')
            ).filter_by(**{
                'semester': semester if semester else self.model_class.semester
            }).first()

            # 平均选课人数
            avg_enrollment_query = db.session.query(
                func.avg(func.count(Enrollment.id))
            ).join(Enrollment, self.model_class.id == Enrollment.course_id)\
             .filter(Enrollment.status == 'approved')

            if semester:
                avg_enrollment_query = avg_enrollment_query.filter(self.model_class.semester == semester)

            avg_enrollment_result = avg_enrollment_query.first()
            avg_enrollment = float(avg_enrollment_result[0]) if avg_enrollment_result[0] else 0

            # 本月新增课程
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_courses_this_month = query.filter(
                self.model_class.created_at >= current_month_start
            ).count()

            return {
                'total_courses': total_courses,
                'new_courses_this_month': new_courses_this_month,
                'category_distribution': {
                    category: count for category, count in category_stats if category
                },
                'status_distribution': {
                    status: count for status, count in status_stats if status
                },
                'credit_statistics': {
                    'total_credits': int(credit_stats.total_credits) if credit_stats.total_credits else 0,
                    'average_credits': round(float(credit_stats.avg_credits), 2) if credit_stats.avg_credits else 0,
                    'min_credits': credit_stats.min_credits,
                    'max_credits': credit_stats.max_credits
                },
                'average_enrollment': round(avg_enrollment, 2)
            }

        except Exception as e:
            self.logger.error(f"获取课程统计失败: {str(e)}")
            raise ServiceError("课程统计服务异常", 'COURSE_STATISTICS_ERROR')

    def get_course_enrollment_trends(self, course_id: int, semesters: int = 6) -> List[Dict[str, Any]]:
        """
        获取课程选课趋势

        Args:
            course_id: 课程ID
            semesters: 学期数量

        Returns:
            List[Dict[str, Any]]: 选课趋势数据
        """
        try:
            course = self.get_by_id(course_id)
            if not course:
                raise NotFoundError("课程")

            # 获取最近几个学期的选课数据
            from ..utils.datetime_utils import AcademicCalendar

            trends = []
            current_year = datetime.now().year
            current_semester = AcademicCalendar.get_current_semester()

            for i in range(semesters):
                # 计算学期
                semester_num = int(current_semester)
                year_offset = (current_semester_num - semester_num + i) // 2
                calc_year = current_year - year_offset

                # 简化的学期计算
                if i % 2 == 0:
                    sem_name = f"{calc_year}-春季学期"
                else:
                    sem_name = f"{calc_year}-秋季学期"

                # 获取该学期的选课人数
                enrollment_count = db.session.query(func.count(Enrollment.id)).filter(
                    and_(
                        Enrollment.course_id == course_id,
                        Enrollment.semester == sem_name,
                        Enrollment.status == 'approved'
                    )
                ).scalar()

                trends.append({
                    'semester': sem_name,
                    'enrollment_count': enrollment_count or 0
                })

            return trends

        except Exception as e:
            self.logger.error(f"获取课程选课趋势失败: {str(e)}", course_id=course_id)
            raise ServiceError("选课趋势查询服务异常", 'ENROLLMENT_TRENDS_ERROR')

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证课程数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'course_code' in data:
                course_code_validation = AcademicValidator.validate_course_code(data['course_code'])
                if not course_code_validation['valid']:
                    raise ValidationError(course_code_validation['message'], 'course_code')

                # 检查课程代码唯一性
                if self.get_by_field('course_code', course_code_validation['normalized']):
                    raise BusinessRuleError("课程代码已存在", 'course_code_exists')

            if 'teacher_id' in data:
                teacher = self.teacher_service.get_by_id(data['teacher_id'])
                if not teacher:
                    raise ValidationError("教师不存在", 'teacher_id')

        elif operation == 'update':
            # 更新时的验证
            if 'course_code' in data:
                course_code_validation = AcademicValidator.validate_course_code(data['course_code'])
                if not course_code_validation['valid']:
                    raise ValidationError(course_code_validation['message'], 'course_code')

                # 检查课程代码唯一性（排除当前课程）
                existing_course = self.get_by_field('course_code', course_code_validation['normalized'])
                if existing_course and existing_course.id != instance.id:
                    raise BusinessRuleError("课程代码已存在", 'course_code_exists')

            if 'teacher_id' in data:
                teacher = self.teacher_service.get_by_id(data['teacher_id'])
                if not teacher:
                    raise ValidationError("教师不存在", 'teacher_id')