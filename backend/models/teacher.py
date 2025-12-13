# ========================================
# 学生信息管理系统 - 教师模型
# ========================================

import enum
from sqlalchemy import Column, String, Date, Enum, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class TeacherStatus(enum.Enum):
    """教师状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    RETIRED = "retired"

class TeacherTitle(enum.Enum):
    """职称枚举"""
    LECTURER = "讲师"
    ASSOCIATE_PROFESSOR = "副教授"
    PROFESSOR = "教授"
    ASSISTANT = "助教"

class Teacher(BaseModel):
    """教师模型"""

    __tablename__ = 'teachers'

    user_id = Column(db.CHAR(36), db.ForeignKey('users.id'), unique=True, nullable=False)

    # 教师信息
    teacher_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Enum(TeacherTitle))
    department = Column(String(100), nullable=False)

    # 联系信息
    office = Column(String(100))
    office_phone = Column(String(20))
    office_hours = Column(Text)  # 办公时间，如：周一、周三 14:00-16:00

    # 专业信息
    specialization = Column(Text)
    research_interests = Column(Text)
    education_background = Column(Text)

    # 工作信息
    hire_date = Column(Date)
    contract_type = Column(String(50))  # 合同类型：全职、兼职等
    status = Column(Enum(TeacherStatus), default=TeacherStatus.ACTIVE)

    # 教学信息
    max_courses_per_semester = Column(db.Integer, default=4)
    current_course_load = Column(db.Integer, default=0)

    # 其他信息
    bio = Column(Text)
    publications = Column(db.JSON)  # 发表论文列表
    projects = Column(db.JSON)  # 参与项目列表
    awards = Column(db.JSON)  # 获奖情况
    social_links = Column(db.JSON)  # 社交媒体链接

    # 关系
    user = relationship("User", backref="teacher_record")
    courses = relationship("Course", back_populates="teacher")
    advisees = relationship("Student", backref="advisor", foreign_keys="Student.advisor_id")

    # 索引
    __table_args__ = (
        Index('idx_teacher_id_department', 'teacher_id', 'department'),
        Index('idx_title_status', 'title', 'status'),
    )

    def __init__(self, **kwargs):
        super(Teacher, self).__init__(**kwargs)
        if not self.status:
            self.status = TeacherStatus.ACTIVE

    @property
    def full_teacher_id(self):
        """获取完整教师编号"""
        return f"T{self.teacher_id.zfill(4)}"

    @property
    def display_title(self):
        """获取显示职称"""
        if self.title:
            return self.title.value
        return "教师"

    @property
    def is_active(self):
        """是否在职教师"""
        return self.status == TeacherStatus.ACTIVE

    @property
    def current_courses(self):
        """获取当前授课课程"""
        from datetime import date
        current_year = date.today().year
        current_month = date.today().month

        if current_month >= 9:
            current_semester = f"{current_year}秋季"
        elif current_month >= 2:
            current_semester = f"{current_year}春季"
        else:
            current_semester = f"{current_year-1}秋季"

        return [course for course in self.courses
                if course.semester == current_semester and course.status == 'active']

    @property
    def total_students(self):
        """获取当前指导的学生总数"""
        return sum([course.current_students or 0 for course in self.current_courses])

    def update_course_load(self):
        """更新当前课程负荷"""
        from datetime import date
        current_year = date.today().year
        current_month = date.today().month

        if current_month >= 9:
            current_semester = f"{current_year}秋季"
        elif current_month >= 2:
            current_semester = f"{current_year}春季"
        else:
            current_semester = f"{current_year-1}秋季"

        self.current_course_load = len([course for course in self.courses
                                       if course.semester == current_semester and course.status == 'active'])
        self.save()

    def can_teach_more_courses(self):
        """检查是否可以承担更多课程"""
        return self.current_course_load < self.max_courses_per_semester

    def get_students_by_course(self, course_id):
        """获取指定课程的学生列表"""
        from .enrollment import Enrollment
        enrollments = Enrollment.query.filter_by(
            course_id=course_id,
            status='enrolled'
        ).all()
        return [enrollment.student for enrollment in enrollments]

    def get_all_advisees(self):
        """获取所有指导学生"""
        active_status = ['enrolled', 'on_leave']
        return [student for student in self.advisees
                if student.academic_status.value in active_status]

    def get_advisees_by_grade(self, grade):
        """获取指定年级的指导学生"""
        return [student for student in self.get_all_advisees()
                if student.grade == grade]

    def add_publication(self, title, authors, journal, year, doi=None):
        """添加发表论文"""
        if not self.publications:
            self.publications = []

        publication = {
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': year,
            'doi': doi
        }

        self.publications.append(publication)
        self.save()

    def remove_publication(self, index):
        """移除论文"""
        if self.publications and 0 <= index < len(self.publications):
            self.publications.pop(index)
            self.save()

    def add_project(self, name, role, start_date, end_date=None, description=None):
        """添加参与项目"""
        if not self.projects:
            self.projects = []

        project = {
            'name': name,
            'role': role,
            'start_date': start_date,
            'end_date': end_date,
            'description': description
        }

        self.projects.append(project)
        self.save()

    def add_award(self, name, issuer, date, level=None):
        """添加获奖记录"""
        if not self.awards:
            self.awards = []

        award = {
            'name': name,
            'issuer': issuer,
            'date': date,
            'level': level
        }

        self.awards.append(award)
        self.save()

    def get_teaching_experience_years(self):
        """获取教学经验年数"""
        if self.hire_date:
            from datetime import date
            return date.today().year - self.hire_date.year
        return 0

    def get_department_colleagues(self):
        """获取同系教师"""
        return Teacher.query.filter(
            Teacher.department == self.department,
            Teacher.user_id != self.user_id,
            Teacher.status == TeacherStatus.ACTIVE
        ).all()

    def get_research_collaborators(self):
        """获取研究合作者"""
        if not self.specialization:
            return []

        # 根据专业领域查找合作者
        return Teacher.query.filter(
            Teacher.specialization.like(f"%{self.specialization}%"),
            Teacher.user_id != self.user_id,
            Teacher.status == TeacherStatus.ACTIVE
        ).limit(10).all()

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        if not include_sensitive:
            # 移除敏感信息
            data.pop('office_phone', None)
        return data

    def __repr__(self):
        return f"<Teacher(teacher_id='{self.teacher_id}', name='{self.user.profile.full_name if self.user.profile else self.user.username}')>"