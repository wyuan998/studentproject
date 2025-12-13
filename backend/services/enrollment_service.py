# ========================================
# 学生信息管理系统 - 选课服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_, func, text

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from .student_service import StudentService
from .course_service import CourseService
from ..models import Enrollment, Student, Course, Teacher, db
from ..utils.logger import get_structured_logger
from ..utils.cache import cache_result
from ..utils.email import send_notification_email


class EnrollmentService(BaseService):
    """选课服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Enrollment
        self.student_service = StudentService()
        self.course_service = CourseService()

    # ========================================
    # 选课管理
    # ========================================

    def create_enrollment(self, enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建选课申请

        Args:
            enrollment_data: 选课数据

        Returns:
            Dict[str, Any]: 创建的选课信息

        Raises:
            ServiceError: 创建失败
        """
        try:
            # 验证必填字段
            required_fields = ['student_id', 'course_id']
            for field in required_fields:
                if field not in enrollment_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证学生存在
            student = self.student_service.get_by_id(enrollment_data['student_id'])
            if not student:
                raise ValidationError("学生不存在", 'student_id')

            # 验证课程存在且开放选课
            course = self.course_service.get_by_id(enrollment_data['course_id'])
            if not course:
                raise ValidationError("课程不存在", 'course_id')

            if course.status != 'active':
                raise BusinessRuleError("课程未开放选课", 'course_not_active')

            # 检查选课权限
            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('enrollment_management')

            # 检查是否已选过该课程
            existing_enrollment = self.model_class.query.filter(
                and_(
                    self.model_class.student_id == enrollment_data['student_id'],
                    self.model_class.course_id == enrollment_data['course_id']
                )
            ).first()

            if existing_enrollment:
                if existing_enrollment.status == 'approved':
                    raise BusinessRuleError("已成功选过该课程", 'already_enrolled')
                elif existing_enrollment.status == 'pending':
                    raise BusinessRuleError("已提交选课申请，请等待审核", 'already_pending')
                elif existing_enrollment.status == 'rejected':
                    # 被拒绝后可以重新申请
                    db.session.delete(existing_enrollment)
                else:
                    raise BusinessRuleError("该课程已有选课记录", 'enrollment_exists')

            # 检查课程容量
            current_enrollments = db.session.query(func.count(self.model_class.id)).filter(
                and_(
                    self.model_class.course_id == enrollment_data['course_id'],
                    self.model_class.status == 'approved'
                )
            ).scalar()

            if current_enrollments >= course.capacity:
                raise BusinessRuleError("课程已满员", 'course_full')

            # 检查时间冲突
            if self._has_schedule_conflict(
                enrollment_data['student_id'],
                enrollment_data['course_id'],
                enrollment_data.get('semester', course.semester)
            ):
                raise BusinessRuleError("课程时间冲突", 'schedule_conflict')

            # 检查先修课程
            if course.prerequisites:
                if not self._check_prerequisites(student.id, course.prerequisites):
                    raise BusinessRuleError("未满足先修课程要求", 'prerequisites_not_met')

            # 创建选课记录
            enrollment = self.model_class()
            enrollment.student_id = enrollment_data['student_id']
            enrollment.course_id = enrollment_data['course_id']
            enrollment.semester = enrollment_data.get('semester', course.semester)
            enrollment.status = 'pending'  # 默认待审核
            enrollment.reason = enrollment_data.get('reason', '')

            enrollment.created_at = datetime.utcnow()

            db.session.add(enrollment)
            db.session.commit()

            # 发送通知给教师
            try:
                if course.teacher and course.teacher.user_id:
                    send_notification_email(
                        course.teacher.email,
                        "新的选课申请",
                        f"学生 {student.name} 申请选课 {course.name}",
                        {
                            'student_name': student.name,
                            'course_name': course.name,
                            'application_time': enrollment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'reason': enrollment.reason
                        }
                    )
            except Exception as e:
                self.logger.warning(f"发送选课通知邮件失败: {str(e)}")

            self._log_business_action('enrollment_created', {
                'enrollment_id': enrollment.id,
                'student_id': student.id,
                'student_name': student.name,
                'course_id': course.id,
                'course_name': course.name,
                'semester': enrollment.semester,
                'status': enrollment.status
            })

            return enrollment.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"创建选课申请失败: {str(e)}", enrollment_data=enrollment_data)
            raise ServiceError("选课申请服务异常", 'ENROLLMENT_CREATE_ERROR')

    def approve_enrollment(self, enrollment_id: int, approve: bool = True, reason: str = None) -> bool:
        """
        审核选课申请

        Args:
            enrollment_id: 选课ID
            approve: 是否批准
            reason: 审核原因

        Returns:
            bool: 是否审核成功

        Raises:
            ServiceError: 审核失败
        """
        try:
            self._check_permission('enrollment_approval')

            enrollment = self.get_by_id(enrollment_id)
            if not enrollment:
                raise NotFoundError("选课记录")

            if enrollment.status not in ['pending']:
                raise BusinessRuleError(f"选课申请状态为 {enrollment.status}，无法审核", 'invalid_status')

            course = self.course_service.get_by_id(enrollment.course_id)
            student = self.student_service.get_by_id(enrollment.student_id)

            if approve:
                # 检查课程容量（再次确认）
                current_enrollments = db.session.query(func.count(self.model_class.id)).filter(
                    and_(
                        self.model_class.course_id == enrollment.course_id,
                        self.model_class.status == 'approved'
                    )
                ).scalar()

                if current_enrollments >= course.capacity:
                    enrollment.status = 'rejected'
                    enrollment.reason = reason or "课程已满员"
                    enrollment.processed_at = datetime.utcnow()
                    enrollment.processed_by = self._get_current_user_id()
                    db.session.commit()

                    # 发送拒绝通知
                    self._send_enrollment_notification(enrollment, student, course, 'rejected', "课程已满员")

                    self._log_business_action('enrollment_rejected', {
                        'enrollment_id': enrollment_id,
                        'student_id': student.id,
                        'course_id': course.id,
                        'reason': "课程已满员"
                    })

                    return False

                enrollment.status = 'approved'
                enrollment.reason = reason or "申请已批准"
                action = 'approved'
            else:
                enrollment.status = 'rejected'
                enrollment.reason = reason or "申请被拒绝"
                action = 'rejected'

            enrollment.processed_at = datetime.utcnow()
            enrollment.processed_by = self._get_current_user_id()
            db.session.commit()

            # 发送通知给学生
            self._send_enrollment_notification(enrollment, student, course, action, enrollment.reason)

            self._log_business_action('enrollment_processed', {
                'enrollment_id': enrollment_id,
                'student_id': student.id,
                'course_id': course.id,
                'action': action,
                'reason': enrollment.reason
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"审核选课申请失败: {str(e)}", enrollment_id=enrollment_id)
            raise ServiceError("选课审核服务异常", 'ENROLLMENT_APPROVAL_ERROR')

    def cancel_enrollment(self, enrollment_id: int, reason: str = None) -> bool:
        """
        取消选课

        Args:
            enrollment_id: 选课ID
            reason: 取消原因

        Returns:
            bool: 是否取消成功

        Raises:
            ServiceError: 取消失败
        """
        try:
            enrollment = self.get_by_id(enrollment_id)
            if not enrollment:
                raise NotFoundError("选课记录")

            # 检查权限（学生本人或管理员）
            current_user_id = self._get_current_user_id()
            student = self.student_service.get_by_id(enrollment.student_id)

            if student.user_id != current_user_id:
                self._check_permission('enrollment_management')

            if enrollment.status == 'cancelled':
                raise BusinessRuleError("选课已取消", 'already_cancelled')

            # 检查是否可以取消（例如，在选课截止日期前）
            course = self.course_service.get_by_id(enrollment.course_id)
            if self._is_past_deadline(course):
                raise BusinessRuleError("已过选课截止日期，无法取消", 'past_deadline')

            # 更新状态
            enrollment.status = 'cancelled'
            enrollment.cancelled_at = datetime.utcnow()
            enrollment.cancelled_by = current_user_id
            enrollment.reason = reason or "学生主动取消"

            db.session.commit()

            # 发送取消通知
            try:
                if course.teacher and course.teacher.email:
                    send_notification_email(
                        course.teacher.email,
                        "选课取消通知",
                        f"学生 {student.name} 已取消选课 {course.name}",
                        {
                            'student_name': student.name,
                            'course_name': course.name,
                            'cancel_time': enrollment.cancelled_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'reason': enrollment.reason
                        }
                    )
            except Exception as e:
                self.logger.warning(f"发送取消通知邮件失败: {str(e)}")

            self._log_business_action('enrollment_cancelled', {
                'enrollment_id': enrollment_id,
                'student_id': student.id,
                'course_id': course.id,
                'reason': enrollment.reason
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"取消选课失败: {str(e)}", enrollment_id=enrollment_id)
            raise ServiceError("选课取消服务异常", 'ENROLLMENT_CANCEL_ERROR')

    # ========================================
    # 批量操作
    # ========================================

    def bulk_approve_enrollments(self, enrollment_ids: List[int], approve: bool = True) -> Dict[str, Any]:
        """
        批量审核选课申请

        Args:
            enrollment_ids: 选课ID列表
            approve: 是否批准

        Returns:
            Dict[str, Any]: 批量处理结果

        Raises:
            ServiceError: 批量处理失败
        """
        try:
            self._check_permission('enrollment_approval')

            processed_count = 0
            failed_count = 0
            errors = []

            for enrollment_id in enrollment_ids:
                try:
                    if self.approve_enrollment(enrollment_id, approve):
                        processed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"选课ID {enrollment_id}: {str(e)}")

            result = {
                'total_count': len(enrollment_ids),
                'processed_count': processed_count,
                'failed_count': failed_count,
                'success': failed_count == 0,
                'errors': errors
            }

            self._log_business_action('bulk_enrollment_processed', {
                'action': 'approved' if approve else 'rejected',
                'total_count': len(enrollment_ids),
                'processed_count': processed_count,
                'failed_count': failed_count
            })

            return result

        except Exception as e:
            self.logger.error(f"批量审核选课失败: {str(e)}", enrollment_ids=enrollment_ids)
            raise ServiceError("批量选课审核服务异常", 'BULK_ENROLLMENT_ERROR')

    def bulk_import_enrollments(self, enrollments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量导入选课数据

        Args:
            enrollments_data: 选课数据列表

        Returns:
            Dict[str, Any]: 导入结果

        Raises:
            ServiceError: 导入失败
        """
        try:
            self._check_permission('enrollment_management')

            imported_count = 0
            failed_count = 0
            errors = []

            for i, enrollment_data in enumerate(enrollments_data):
                try:
                    # 设置状态为直接批准（批量导入）
                    enrollment_data['status'] = 'approved'
                    enrollment = self.create_enrollment(enrollment_data)

                    # 更新为已批准状态
                    enrollment.status = 'approved'
                    enrollment.processed_at = datetime.utcnow()
                    enrollment.processed_by = self._get_current_user_id()
                    db.session.commit()

                    imported_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第 {i+1} 行: {str(e)}")
                    db.session.rollback()

            result = {
                'total_count': len(enrollments_data),
                'imported_count': imported_count,
                'failed_count': failed_count,
                'success': failed_count == 0,
                'errors': errors
            }

            self._log_business_action('bulk_enrollments_imported', {
                'total_count': len(enrollments_data),
                'imported_count': imported_count,
                'failed_count': failed_count
            })

            return result

        except Exception as e:
            self.logger.error(f"批量导入选课失败: {str(e)}")
            raise ServiceError("批量选课导入服务异常", 'BULK_IMPORT_ERROR')

    # ========================================
    # 选课查询
    # ========================================

    @cache_result(timeout=300)  # 5分钟缓存
    def get_student_enrollments(
        self,
        student_id: int,
        semester: str = None,
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取学生选课列表

        Args:
            student_id: 学生ID
            semester: 学期筛选
            status: 状态筛选
            page: 页码
            per_page: 每页数量

        Returns:
            Dict[str, Any]: 选课列表和分页信息
        """
        try:
            # 检查权限
            student = self.student_service.get_by_id(student_id)
            if not student:
                raise NotFoundError("学生")

            current_user_id = self._get_current_user_id()
            if student.user_id != current_user_id:
                self._check_permission('enrollment_management')

            # 构建查询
            filters = {'student_id': student_id}
            if semester:
                filters['semester'] = semester
            if status:
                filters['status'] = status

            result = self.get_list(
                filters=filters,
                page=page,
                per_page=per_page,
                sort_by='created_at',
                sort_order='desc'
            )

            # 为每个选课记录添加课程信息
            enrollments_with_details = []
            for enrollment in result['items']:
                enrollment_dict = enrollment.to_dict()

                # 获取课程信息
                course = self.course_service.get_by_id(enrollment.course_id)
                if course:
                    enrollment_dict['course'] = {
                        'id': course.id,
                        'course_code': course.course_code,
                        'name': course.name,
                        'credits': course.credits,
                        'teacher_name': course.teacher.name if course.teacher else None,
                        'category': course.category,
                        'semester': course.semester
                    }

                enrollments_with_details.append(enrollment_dict)

            result['items'] = enrollments_with_details
            return result

        except Exception as e:
            self.logger.error(f"获取学生选课列表失败: {str(e)}", student_id=student_id)
            raise ServiceError("学生选课查询服务异常", 'STUDENT_ENROLLMENTS_ERROR')

    def get_course_enrollments(
        self,
        course_id: int,
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取课程选课列表

        Args:
            course_id: 课程ID
            status: 状态筛选
            page: 页码
            per_page: 每页数量

        Returns:
            Dict[str, Any]: 选课列表和分页信息
        """
        try:
            # 检查权限
            course = self.course_service.get_by_id(course_id)
            if not course:
                raise NotFoundError("课程")

            current_user_id = self._get_current_user_id()
            if course.teacher_id != current_user_id:
                self._check_permission('enrollment_management')

            # 构建查询
            filters = {'course_id': course_id}
            if status:
                filters['status'] = status

            result = self.get_list(
                filters=filters,
                page=page,
                per_page=per_page,
                sort_by='created_at',
                sort_order='desc'
            )

            # 为每个选课记录添加学生信息
            enrollments_with_details = []
            for enrollment in result['items']:
                enrollment_dict = enrollment.to_dict()

                # 获取学生信息
                student = self.student_service.get_by_id(enrollment.student_id)
                if student:
                    enrollment_dict['student'] = {
                        'id': student.id,
                        'student_id': student.student_id,
                        'name': student.name,
                        'grade_level': student.grade_level,
                        'department': student.department,
                        'major': student.major
                    }

                enrollments_with_details.append(enrollment_dict)

            result['items'] = enrollments_with_details
            return result

        except Exception as e:
            self.logger.error(f"获取课程选课列表失败: {str(e)}", course_id=course_id)
            raise ServiceError("课程选课查询服务异常", 'COURSE_ENROLLMENTS_ERROR')

    # ========================================
    # 选课统计
    # ========================================

    def get_enrollment_statistics(self, semester: str = None, department: str = None) -> Dict[str, Any]:
        """
        获取选课统计信息

        Args:
            semester: 学期筛选
            department: 院系筛选

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 基础查询
            query = self.model_class.query

            if semester:
                query = query.filter(self.model_class.semester == semester)

            # 通过学生院系筛选
            if department:
                query = query.join(Student).filter(Student.department == department)

            # 总数统计
            total_enrollments = query.count()

            # 按状态统计
            status_stats = db.session.query(
                self.model_class.status,
                func.count(self.model_class.id)
            ).filter_by(**{
                'semester': semester if semester else self.model_class.semester
            }).group_by(self.model_class.status).all()

            # 按课程类别统计
            category_stats = db.session.query(
                Course.category,
                func.count(self.model_class.id)
            ).join(Course, self.model_class.course_id == Course.id)\
             .filter_by(**{
                 'semester': semester if semester else self.model_class.semester
             }).group_by(Course.category).all()

            # 本月新增选课
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_enrollments_this_month = query.filter(
                self.model_class.created_at >= current_month_start
            ).count()

            # 待处理申请数
            pending_count = query.filter(self.model_class.status == 'pending').count()

            return {
                'total_enrollments': total_enrollments,
                'new_enrollments_this_month': new_enrollments_this_month,
                'pending_applications': pending_count,
                'status_distribution': {
                    status: count for status, count in status_stats if status
                },
                'category_distribution': {
                    category: count for category, count in category_stats if category
                }
            }

        except Exception as e:
            self.logger.error(f"获取选课统计失败: {str(e)}")
            raise ServiceError("选课统计服务异常", 'ENROLLMENT_STATISTICS_ERROR')

    # ========================================
    # 辅助方法
    # ========================================

    def _has_schedule_conflict(self, student_id: int, course_id: int, semester: str) -> bool:
        """
        检查时间冲突

        Args:
            student_id: 学生ID
            course_id: 课程ID
            semester: 学期

        Returns:
            bool: 是否有冲突
        """
        # 这里需要根据实际的课程时间表数据结构来实现
        # 简化版本：检查是否已在同一学期选过同一教师的课程
        course = self.course_service.get_by_id(course_id)

        conflict_enrollment = self.model_class.query.filter(
            and_(
                self.model_class.student_id == student_id,
                self.model_class.semester == semester,
                self.model_class.status == 'approved'
            )
        ).join(Course, self.model_class.course_id == Course.id)\
         .filter(Course.teacher_id == course.teacher_id).first()

        return conflict_enrollment is not None

    def _check_prerequisites(self, student_id: int, prerequisites: str) -> bool:
        """
        检查先修课程要求

        Args:
            student_id: 学生ID
            prerequisites: 先修课程要求

        Returns:
            bool: 是否满足要求
        """
        if not prerequisites:
            return True

        # 简化版本：检查学生是否已通过先修课程
        # 实际实现需要解析prerequisites并检查学生成绩记录
        # 这里假设prerequisites是课程代码列表，用逗号分隔
        prerequisite_courses = [code.strip() for code in prerequisites.split(',') if code.strip()]

        for course_code in prerequisite_courses:
            # 查找该课程的通过记录
            prerequisite_course = self.course_service.model_class.query.filter_by(
                course_code=course_code
            ).first()

            if prerequisite_course:
                passed_grade = db.session.query(Grade).filter(
                    and_(
                        Grade.student_id == student_id,
                        Grade.course_id == prerequisite_course.id,
                        Grade.score >= 60  # 及格分数
                    )
                ).first()

                if not passed_grade:
                    return False

        return True

    def _is_past_deadline(self, course: Any) -> bool:
        """
        检查是否已过选课截止日期

        Args:
            course: 课程对象

        Returns:
            bool: 是否已过截止日期
        """
        # 这里需要根据实际业务规则实现
        # 例如：开学前一周截止选课
        from ..utils.datetime_utils import AcademicCalendar

        current_semester = AcademicCalendar.get_current_semester()
        current_year = datetime.now().year

        # 简化版本：如果课程已开始，则不能取消
        semester_start = AcademicCalendar.get_semester_range(current_year, current_semester)[0]
        return datetime.utcnow() > semester_start

    def _send_enrollment_notification(self, enrollment: Any, student: Any, course: Any, action: str, reason: str):
        """
        发送选课通知

        Args:
            enrollment: 选课记录
            student: 学生
            course: 课程
            action: 操作类型
            reason: 原因
        """
        try:
            if action == 'approved':
                subject = "选课申请已批准"
                message = f"恭喜！您选课 {course.name} 的申请已获批准。"
            elif action == 'rejected':
                subject = "选课申请被拒绝"
                message = f"很遗憾，您选课 {course.name} 的申请被拒绝。原因：{reason}"
            else:
                return

            # 发送邮件通知给学生
            if student.email:
                send_notification_email(
                    student.email,
                    subject,
                    message,
                    {
                        'student_name': student.name,
                        'course_name': course.name,
                        'action': action,
                        'reason': reason,
                        'notification_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )

        except Exception as e:
            self.logger.warning(f"发送选课通知失败: {str(e)}")

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证选课数据

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

                if course.status != 'active':
                    raise ValidationError("课程未开放选课", 'course_id')