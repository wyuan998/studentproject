# ========================================
# 学生信息管理系统 - 学生模型
# ========================================

import enum
from sqlalchemy import Column, String, Integer, Float, Date, Enum, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class AcademicStatus(enum.Enum):
    """学业状态枚举"""
    ENROLLED = "enrolled"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"
    ON_LEAVE = "on_leave"

class Student(BaseModel):
    """学生模型"""

    __tablename__ = 'students'

    user_id = Column(db.CHAR(36), db.ForeignKey('users.id'), unique=True, nullable=False)

    # 学号信息
    student_id = Column(String(20), unique=True, nullable=False, index=True)

    # 班级信息
    grade = Column(String(10), nullable=False)  # 年级
    class_name = Column(String(50), nullable=False)  # 班级

    # 专业信息
    major = Column(String(100), nullable=False)
    minor = Column(String(100))

    # 学业信息
    enrollment_date = Column(Date, nullable=False)
    expected_graduation_date = Column(Date)
    academic_status = Column(Enum(AcademicStatus), default=AcademicStatus.ENROLLED)

    # 学业表现
    gpa = Column(Float)
    total_credits = Column(Integer, default=0)
    credits_earned = Column(Integer, default=0)
    credits_in_progress = Column(Integer, default=0)

    # 辅导员信息
    advisor_id = Column(db.CHAR(36), db.ForeignKey('teachers.id'))

    # 其他信息
    notes = Column(db.Text)
    tags = Column(db.JSON)  # 标签，如：优秀学生、奖学金获得者等

    # 关系
    user = relationship("User", backref="student_record")
    advisor = relationship("Teacher", backref="advisees")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")

    # 约束
    __table_args__ = (
        CheckConstraint('gpa >= 0 AND gpa <= 4.0', name='check_gpa_range'),
        CheckConstraint('credits_earned >= 0', name='check_credits_earned_positive'),
        CheckConstraint('credits_in_progress >= 0', name='check_credits_in_progress_positive'),
        Index('idx_student_id_grade', 'student_id', 'grade'),
        Index('idx_major_academic_status', 'major', 'academic_status'),
    )

    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        if not self.academic_status:
            self.academic_status = AcademicStatus.ENROLLED

    @property
    def full_student_id(self):
        """获取完整学号（可能包含年级前缀）"""
        if self.grade and not self.student_id.startswith(self.grade):
            return f"{self.grade}{self.student_id}"
        return self.student_id

    @property
    def class_display(self):
        """获取班级显示名称"""
        return f"{self.grade}{self.class_name}"

    @property
    def is_active(self):
        """是否在读学生"""
        return self.academic_status in [AcademicStatus.ENROLLED, AcademicStatus.ON_LEAVE]

    @property
    def academic_progress(self):
        """学业进度百分比"""
        if self.expected_graduation_date and self.enrollment_date:
            from datetime import date
            total_days = (self.expected_graduation_date - self.enrollment_date).days
            if total_days > 0:
                elapsed_days = (date.today() - self.enrollment_date).days
                return min(100, (elapsed_days / total_days) * 100)
        return 0

    def update_gpa(self):
        """更新GPA"""
        from sqlalchemy import func
        from .grade import Grade, GradeType

        # 计算加权平均分
        grade_query = db.session.query(
            func.sum(Grade.score * Grade.weight).label('weighted_sum'),
            func.sum(Grade.weight).label('total_weight')
        ).filter(
            Grade.student_id == self.id,
            Grade.exam_type.in_([GradeType.MIDTERM, GradeType.FINAL]),
            Grade.score.isnot(None)
        )

        result = grade_query.first()
        if result and result.total_weight and result.total_weight > 0:
            weighted_average = result.weighted_sum / result.total_weight
            # 转换为4.0制GPA（这里使用简单的线性转换）
            self.gpa = round((weighted_average / 100) * 4.0, 2)
        else:
            self.gpa = None

        self.save()

    def update_credits(self):
        """更新学分信息"""
        from sqlalchemy import func
        from .enrollment import Enrollment
        from .grade import Grade, GradeType

        # 获取已修读课程的总学分
        completed_courses = db.session.query(
            func.sum(func.cofunc.credits).label('total_credits')
        ).join(Grade).filter(
            Enrollment.student_id == self.id,
            Enrollment.status == 'completed',
            Grade.exam_type == GradeType.FINAL,
            Grade.score >= 60  # 及格
        ).first()

        # 获取正在修读的课程学分
        in_progress_courses = db.session.query(
            func.sum(func.cofunc.credits).label('total_credits')
        ).filter(
            Enrollment.student_id == self.id,
            Enrollment.status == 'enrolled'
        ).first()

        self.credits_earned = completed_courses.total_credits or 0
        self.credits_in_progress = in_progress_courses.total_credits or 0
        self.total_credits = self.credits_earned + self.credits_in_progress

        self.save()

    def get_current_semester_courses(self):
        """获取当前学期课程"""
        from datetime import date
        current_year = date.today().year
        current_month = date.today().month

        if current_month >= 9:
            current_semester = f"{current_year}秋季"
        elif current_month >= 2:
            current_semester = f"{current_year}春季"
        else:
            current_semester = f"{current_year-1}秋季"

        return [enrollment.course for enrollment in self.enrollments
                if enrollment.semester == current_semester and enrollment.status == 'enrolled']

    def get_course_grades(self, course_id):
        """获取指定课程的所有成绩"""
        from .grade import Grade
        return Grade.query.filter_by(
            student_id=self.id,
            course_id=course_id
        ).order_by(Grade.created_at).all()

    def calculate_semester_gpa(self, semester):
        """计算指定学期的GPA"""
        from sqlalchemy import func
        from .grade import Grade, GradeType

        result = db.session.query(
            func.sum(Grade.score * Grade.weight).label('weighted_sum'),
            func.sum(Grade.weight).label('total_weight')
        ).join(Enrollment).filter(
            Grade.student_id == self.id,
            Enrollment.semester == semester,
            Grade.exam_type.in_([GradeType.MIDTERM, GradeType.FINAL]),
            Grade.score.isnot(None)
        ).first()

        if result and result.total_weight and result.total_weight > 0:
            weighted_average = result.weighted_sum / result.total_weight
            return round((weighted_average / 100) * 4.0, 2)
        return None

    def add_tag(self, tag):
        """添加标签"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()

    def remove_tag(self, tag):
        """移除标签"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.save()

    def get_honors(self):
        """获取荣誉信息"""
        honors = []
        if self.tags:
            if '优秀学生' in self.tags:
                honors.append('优秀学生')
            if '奖学金获得者' in self.tags:
                honors.append('奖学金获得者')
        if self.gpa and self.gpa >= 3.5:
            honors.append('学习优秀')
        return honors

    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', name='{self.user.profile.full_name if self.user.profile else self.user.username}')>"