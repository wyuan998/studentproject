# ========================================
# 学生信息管理系统 - 课程模型
# ========================================

import enum
from sqlalchemy import Column, String, Integer, Float, Text, Enum, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class CourseType(enum.Enum):
    """课程类型枚举"""
    REQUIRED = "required"  # 必修课
    ELECTIVE = "elective"  # 选修课
    PROFESSIONAL = "professional"  # 专业课
    GENERAL = "general"  # 通识课

class CourseStatus(enum.Enum):
    """课程状态枚举"""
    ACTIVE = "active"  # 开课中
    INACTIVE = "inactive"  # 未开课
    COMPLETED = "completed"  # 已结束
    CANCELLED = "cancelled"  # 已取消
PLANNING = "planning"  # 计划中

class Course(BaseModel):
    """课程模型"""

    __tablename__ = 'courses'

    # 基本信息
    course_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # 课程属性
    credits = Column(Float, nullable=False)
    hours_per_week = Column(Integer, nullable=False)
    total_hours = Column(Integer)

    # 分类信息
    course_type = Column(Enum(CourseType), nullable=False)
    category = Column(String(50))  # 课程分类
    level = Column(String(20))  # 课程级别：本科、研究生等

    # 学期信息
    semester = Column(String(20), nullable=False)  # 如：2024春季、2024秋季
    academic_year = Column(String(10))  # 学年

    # 人数限制
    max_students = Column(Integer, default=50)
    min_students = Column(Integer, default=5)
    current_students = Column(Integer, default=0)

    # 教师信息
    teacher_id = Column(db.CHAR(36), db.ForeignKey('teachers.id'))

    # 时间安排
    schedule = Column(JSON)  # 上课时间安排
    classroom = Column(String(100))  # 教室
    campus = Column(String(50))  # 校区

    # 课程要求
    prerequisites = Column(JSON)  # 先修课程
    restrictions = Column(Text)  # 选课限制
    materials = Column(JSON)  # 课程材料

    # 状态和设置
    status = Column(Enum(CourseStatus), default=CourseStatus.PLANNING)
    is_online = Column(Boolean, default=False)
    allow_auditing = Column(Boolean, default=False)  # 是否允许旁听

    # 评分设置
    grading_scheme = Column(JSON)  # 评分方案
    passing_score = Column(Float, default=60.0)

    # 其他信息
    syllabus = Column(Text)  # 课程大纲
    objectives = Column(Text)  # 课程目标
    outcomes = Column(Text)  # 学习成果
    notes = Column(Text)  # 备注

    # 关系
    teacher = relationship("Teacher", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="course", cascade="all, delete-orphan")

    # 约束
    __table_args__ = (
        CheckConstraint('credits > 0 AND credits <= 10', name='check_credits_range'),
        CheckConstraint('hours_per_week > 0', name='check_hours_positive'),
        CheckConstraint('max_students > 0', name='check_max_students_positive'),
        CheckConstraint('min_students >= 0', name='check_min_students_positive'),
        CheckConstraint('passing_score >= 0 AND passing_score <= 100', name='check_passing_score_range'),
        Index('idx_course_code_semester', 'course_code', 'semester'),
        Index('idx_teacher_semester', 'teacher_id', 'semester'),
        Index('idx_type_status', 'course_type', 'status'),
    )

    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)

        # 设置默认评分方案
        if not self.grading_scheme:
            self.grading_scheme = {
                'attendance': 0.1,      # 出勤 10%
                'assignment': 0.3,      # 作业 30%
                'midterm': 0.3,         # 期中 30%
                'final': 0.3           # 期末 30%
            }

        # 计算总课时
        if self.hours_per_week and self.semester:
            if '春季' in self.semester or '秋季' in self.semester:
                self.total_hours = self.hours_per_week * 16  # 16周
            elif '夏季' in self.semester:
                self.total_hours = self.hours_per_week * 8   # 8周

    @property
    def full_course_code(self):
        """获取完整课程代码"""
        return f"{self.course_code}-{self.semester}"

    @property
    def is_full(self):
        """检查是否已满员"""
        return self.current_students >= self.max_students

    @property
    def can_enroll(self):
        """检查是否可以选课"""
        return (
            self.status == CourseStatus.ACTIVE and
            not self.is_full and
            self.current_students < self.min_students or self.current_students >= self.min_students
        )

    @property
    def enrollment_rate(self):
        """获取选课率"""
        if self.max_students > 0:
            return (self.current_students / self.max_students) * 100
        return 0

    @property
    def display_type(self):
        """获取课程类型显示名称"""
        type_mapping = {
            CourseType.REQUIRED: "必修课",
            CourseType.ELECTIVE: "选修课",
            CourseType.PROFESSIONAL: "专业课",
            CourseType.GENERAL: "通识课"
        }
        return type_mapping.get(self.course_type, "课程")

    @property
    def display_status(self):
        """获取课程状态显示名称"""
        status_mapping = {
            CourseStatus.ACTIVE: "开课中",
            CourseStatus.INACTIVE: "未开课",
            CourseStatus.COMPLETED: "已结束",
            CourseStatus.CANCELLED: "已取消",
            CourseStatus.PLANNING: "计划中"
        }
        return status_mapping.get(self.status, "未知")

    def update_current_students(self):
        """更新当前选课人数"""
        from .enrollment import Enrollment
        active_enrollments = Enrollment.query.filter_by(
            course_id=self.id,
            status='enrolled'
        ).count()
        self.current_students = active_enrollments
        self.save()

    def get_enrolled_students(self):
        """获取已选课的学生列表"""
        from .enrollment import Enrollment
        enrollments = Enrollment.query.filter_by(
            course_id=self.id,
            status='enrolled'
        ).all()
        return [enrollment.student for enrollment in enrollments]

    def get_waitlist_students(self):
        """获取候补学生列表"""
        from .enrollment import Enrollment
        enrollments = Enrollment.query.filter_by(
            course_id=self.id,
            status='waitlist'
        ).all()
        return [enrollment.student for enrollment in enrollments]

    def can_student_enroll(self, student):
        """检查学生是否可以选课"""
        # 检查先修课程
        if self.prerequisites:
            completed_prereqs = student.get_completed_prerequisites()
            for prereq in self.prerequisites:
                if prereq not in completed_prereqs:
                    return False, f"缺少先修课程: {prereq}"

        # 检查是否已选过
        from .enrollment import Enrollment
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=self.id
        ).first()

        if existing_enrollment:
            if existing_enrollment.status == 'enrolled':
                return False, "已经选过此课程"
            elif existing_enrollment.status == 'completed':
                return False, "已经完成此课程"
            elif existing_enrollment.status == 'dropped':
                return False, "已退选此课程"

        # 检查人数限制
        if self.is_full:
            return False, "课程已满员"

        return True, "可以选课"

    def add_prerequisite(self, course_code):
        """添加先修课程"""
        if not self.prerequisites:
            self.prerequisites = []
        if course_code not in self.prerequisites:
            self.prerequisites.append(course_code)
            self.save()

    def remove_prerequisite(self, course_code):
        """移除先修课程"""
        if self.prerequisites and course_code in self.prerequisites:
            self.prerequisites.remove(course_code)
            self.save()

    def update_grading_scheme(self, scheme_dict):
        """更新评分方案"""
        # 验证评分方案总和为1
        total = sum(scheme_dict.values())
        if abs(total - 1.0) > 0.01:  # 允许0.01的误差
            raise ValueError("评分方案权重总和必须为1.0")

        self.grading_scheme = scheme_dict
        self.save()

    def get_final_grades(self):
        """获取所有学生的最终成绩"""
        from .grade import Grade, GradeType
        return Grade.query.filter_by(
            course_id=self.id,
            exam_type=GradeType.FINAL
        ).all()

    def calculate_class_average(self, exam_type):
        """计算班级平均分"""
        from .grade import Grade
        grades = Grade.query.filter_by(
            course_id=self.id,
            exam_type=exam_type
        ).filter(Grade.score.isnot(None)).all()

        if not grades:
            return None

        return sum(grade.score for grade in grades) / len(grades)

    def get_grade_distribution(self, exam_type):
        """获取成绩分布"""
        from .grade import Grade
        grades = Grade.query.filter_by(
            course_id=self.id,
            exam_type=exam_type
        ).filter(Grade.score.isnot(None)).all()

        if not grades:
            return {}

        distribution = {
            'A (90-100)': 0,
            'B (80-89)': 0,
            'C (70-79)': 0,
            'D (60-69)': 0,
            'F (0-59)': 0
        }

        for grade in grades:
            if grade.score >= 90:
                distribution['A (90-100)'] += 1
            elif grade.score >= 80:
                distribution['B (80-89)'] += 1
            elif grade.score >= 70:
                distribution['C (70-79)'] += 1
            elif grade.score >= 60:
                distribution['D (60-69)'] += 1
            else:
                distribution['F (0-59)'] += 1

        return distribution

    def duplicate_for_semester(self, new_semester, new_teacher_id=None):
        """为新学期复制课程"""
        new_course = Course(
            course_code=self.course_code,
            name=self.name,
            description=self.description,
            credits=self.credits,
            hours_per_week=self.hours_per_week,
            course_type=self.course_type,
            category=self.category,
            level=self.level,
            semester=new_semester,
            academic_year=new_semester.split('年')[0] if '年' in new_semester else None,
            max_students=self.max_students,
            min_students=self.min_students,
            teacher_id=new_teacher_id or self.teacher_id,
            prerequisites=self.prerequisites,
            restrictions=self.restrictions,
            materials=self.materials,
            grading_scheme=self.grading_scheme,
            passing_score=self.passing_score,
            syllabus=self.syllabus,
            objectives=self.objectives,
            outcomes=self.outcomes,
            is_online=self.is_online,
            allow_auditing=self.allow_auditing,
            status=CourseStatus.PLANNING
        )
        new_course.save()
        return new_course

    def to_dict(self, include_details=True):
        """转换为字典"""
        data = super().to_dict()
        if include_details:
            data['enrollment_rate'] = self.enrollment_rate
            data['display_type'] = self.display_type
            data['display_status'] = self.display_status
        return data

    def __repr__(self):
        return f"<Course(course_code='{self.course_code}', name='{self.name}', semester='{self.semester}')>"