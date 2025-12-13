# ========================================
# 学生信息管理系统 - 选课模型
# ========================================

import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, CheckConstraint, Text
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class EnrollmentStatus(enum.Enum):
    """选课状态枚举"""
    ENROLLED = "enrolled"  # 已选课
    WAITLIST = "waitlist"  # 候补
    DROPPED = "dropped"  # 已退选
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 不及格
    AUDITING = "auditing"  # 旁听

class Enrollment(BaseModel):
    """选课模型"""

    __tablename__ = 'enrollments'

    # 关联信息
    student_id = Column(db.CHAR(36), db.ForeignKey('students.id'), nullable=False)
    course_id = Column(db.CHAR(36), db.ForeignKey('courses.id'), nullable=False)

    # 选课信息
    semester = Column(String(20), nullable=False)  # 学期
    enrollment_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 状态信息
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ENROLLED)

    # 时间信息
    drop_date = Column(DateTime)  # 退选时间
    complete_date = Column(DateTime)  # 完成时间

    # 成绩信息
    final_score = Column(db.Float)  # 最终成绩
    grade_point = Column(db.Float)  # 绩点
    letter_grade = Column(String(2))  # 等级成绩 A, B, C, D, F

    # 考勤信息
    attendance_count = Column(db.Integer, default=0)  # 出勤次数
    total_classes = Column(db.Integer, default=0)  # 总课时
    tardy_count = Column(db.Integer, default=0)  # 迟到次数
    absence_count = Column(db.Integer, default=0)  # 缺勤次数

    # 选课类型
    enrollment_type = Column(String(20), default='regular')  # regular, retake, audit
    priority = Column(db.Integer, default=0)  # 选课优先级

    # 审核信息
    is_approved = Column(db.Boolean, default=True)  # 是否已审核
    approved_by = Column(db.CHAR(36), db.ForeignKey('users.id'))  # 审核人
    approved_at = Column(DateTime)  # 审核时间
    approval_notes = Column(Text)  # 审核备注

    # 其他信息
    notes = Column(Text)  # 备注
    special_needs = Column(Text)  # 特殊需求

    # 关系
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    approver = relationship("User", foreign_keys=[approved_by])

    # 索引和约束
    __table_args__ = (
        Index('idx_student_course_semester', 'student_id', 'course_id', 'semester'),
        Index('idx_course_semester_status', 'course_id', 'semester', 'status'),
        Index('idx_student_semester_status', 'student_id', 'semester', 'status'),
        Index('idx_enrollment_date', 'enrollment_date'),
        CheckConstraint('final_score >= 0 AND final_score <= 100', name='check_final_score_range'),
        CheckConstraint('grade_point >= 0 AND grade_point <= 4.0', name='check_grade_point_range'),
        CheckConstraint('attendance_count >= 0', name='check_attendance_positive'),
        CheckConstraint('tardy_count >= 0', name='check_tardy_positive'),
        CheckConstraint('absence_count >= 0', name='check_absence_positive'),
    )

    def __init__(self, **kwargs):
        super(Enrollment, self).__init__(**kwargs)
        if not self.enrollment_date:
            self.enrollment_date = datetime.utcnow()

    @property
    def is_active(self):
        """是否为活跃选课"""
        return self.status == EnrollmentStatus.ENROLLED

    @property
    def is_completed(self):
        """是否已完成课程"""
        return self.status == EnrollmentStatus.COMPLETED

    @property
    def attendance_rate(self):
        """出勤率"""
        if self.total_classes > 0:
            return (self.attendance_count / self.total_classes) * 100
        return 0

    @property
    def display_status(self):
        """获取状态显示名称"""
        status_mapping = {
            EnrollmentStatus.ENROLLED: "已选课",
            EnrollmentStatus.WAITLIST: "候补中",
            EnrollmentStatus.DROPPED: "已退选",
            EnrollmentStatus.COMPLETED: "已完成",
            EnrollmentStatus.FAILED: "不及格",
            EnrollmentStatus.AUDITING: "旁听中"
        }
        return status_mapping.get(self.status, "未知")

    @property
    def display_grade(self):
        """获取成绩显示"""
        if self.final_score is not None:
            return f"{self.final_score:.1f} ({self.letter_grade or 'N/A'})"
        elif self.status == EnrollmentStatus.COMPLETED:
            return "完成"
        elif self.status == EnrollmentStatus.FAILED:
            return "不及格"
        else:
            return "未评分"

    def drop_course(self, reason=None):
        """退选课程"""
        self.status = EnrollmentStatus.DROPPED
        self.drop_date = datetime.utcnow()
        if reason:
            self.notes = reason
        self.save()

        # 更新课程选课人数
        self.course.update_current_students()

    def complete_course(self, final_score=None):
        """完成课程"""
        self.status = EnrollmentStatus.COMPLETED
        self.complete_date = datetime.utcnow()

        if final_score is not None:
            self.final_score = final_score
            self.grade_point = self._calculate_grade_point(final_score)
            self.letter_grade = self._calculate_letter_grade(final_score)

        self.save()

    def approve(self, approver_id, notes=None):
        """审核通过"""
        self.is_approved = True
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        self.save()

    def reject(self, approver_id, notes):
        """审核拒绝"""
        self.is_approved = False
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        self.save()

    def _calculate_grade_point(self, score):
        """计算绩点"""
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 82:
            return 3.3
        elif score >= 78:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 72:
            return 2.3
        elif score >= 68:
            return 2.0
        elif score >= 64:
            return 1.5
        elif score >= 60:
            return 1.0
        else:
            return 0.0

    def _calculate_letter_grade(self, score):
        """计算等级成绩"""
        if score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 82:
            return "B+"
        elif score >= 78:
            return "B"
        elif score >= 75:
            return "B-"
        elif score >= 72:
            return "C+"
        elif score >= 68:
            return "C"
        elif score >= 64:
            return "C-"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def record_attendance(self, present=True, tardy=False):
        """记录考勤"""
        self.total_classes += 1
        if present:
            self.attendance_count += 1
            if tardy:
                self.tardy_count += 1
        else:
            self.absence_count += 1
        self.save()

    def get_course_grades(self):
        """获取此课程的所有成绩记录"""
        from .grade import Grade
        return Grade.query.filter_by(
            student_id=self.student_id,
            course_id=self.course_id
        ).order_by(Grade.created_at).all()

    def calculate_final_score(self):
        """计算最终成绩"""
        grades = self.get_course_grades()
        if not grades or not self.course.grading_scheme:
            return None

        scheme = self.course.grading_scheme
        total_score = 0

        for grade in grades:
            if grade.exam_type in scheme and grade.score is not None:
                weight = scheme[grade.exam_type]
                total_score += grade.score * weight

        return min(100, max(0, total_score))  # 确保成绩在0-100范围内

    def update_final_score(self):
        """更新最终成绩"""
        final_score = self.calculate_final_score()
        if final_score is not None:
            self.final_score = final_score
            self.grade_point = self._calculate_grade_point(final_score)
            self.letter_grade = self._calculate_letter_grade(final_score)
            self.save()

    def can_drop(self, deadline=None):
        """检查是否可以退选"""
        # 检查状态
        if self.status not in [EnrollmentStatus.ENROLLED, EnrollmentStatus.WAITLIST]:
            return False, "当前状态不允许退选"

        # 检查截止日期
        if deadline and datetime.utcnow() > deadline:
            return False, "已超过退选截止日期"

        # 检查是否已有成绩
        if self.final_score is not None:
            return False, "已有成绩记录，无法退选"

        return True, "可以退选"

    def is_retake(self):
        """是否为重修"""
        return self.enrollment_type == 'retake'

    def is_audit(self):
        """是否为旁听"""
        return self.enrollment_type == 'audit'

    def get_attendance_summary(self):
        """获取出勤摘要"""
        return {
            'total_classes': self.total_classes,
            'attendance_count': self.attendance_count,
            'tardy_count': self.tardy_count,
            'absence_count': self.absence_count,
            'attendance_rate': self.attendance_rate
        }

    def to_dict(self, include_student=True, include_course=True):
        """转换为字典"""
        data = super().to_dict()
        data['display_status'] = self.display_status
        data['display_grade'] = self.display_grade
        data['attendance_rate'] = self.attendance_rate

        if include_student and self.student:
            data['student'] = {
                'id': self.student.id,
                'student_id': self.student.student_id,
                'name': self.student.user.profile.full_name if self.student.user.profile else self.student.user.username
            }

        if include_course and self.course:
            data['course'] = {
                'id': self.course.id,
                'course_code': self.course.course_code,
                'name': self.course.name,
                'credits': self.course.credits,
                'teacher': self.course.teacher.user.profile.full_name if self.course.teacher and self.course.teacher.user.profile else None
            }

        return data

    @classmethod
    def get_student_enrollments(cls, student_id, semester=None, status=None):
        """获取学生的选课记录"""
        query = cls.query.filter_by(student_id=student_id)

        if semester:
            query = query.filter_by(semester=semester)
        if status:
            query = query.filter_by(status=status)

        return query.order_by(cls.enrollment_date.desc()).all()

    @classmethod
    def get_course_enrollments(cls, course_id, status=None):
        """获取课程的选课记录"""
        query = cls.query.filter_by(course_id=course_id)

        if status:
            query = query.filter_by(status=status)

        return query.order_by(cls.enrollment_date.asc()).all()

    @classmethod
    def get_semester_enrollments(cls, semester, status=None):
        """获取学期的选课记录"""
        query = cls.query.filter_by(semester=semester)

        if status:
            query = query.filter_by(status=status)

        return query.order_by(cls.enrollment_date.desc()).all()

    def __repr__(self):
        return f"<Enrollment(student='{self.student.student_id if self.student else 'Unknown'}', course='{self.course.course_code if self.course else 'Unknown'}', status='{self.status.value}')>"