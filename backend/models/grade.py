# ========================================
# 学生信息管理系统 - 成绩模型
# ========================================

import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Index, CheckConstraint, Text
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class GradeType(enum.Enum):
    """成绩类型枚举"""
    QUIZ = "quiz"              # 测验
    ASSIGNMENT = "assignment"  # 作业
    MIDTERM = "midterm"        # 期中考试
    FINAL = "final"            # 期末考试
    PROJECT = "project"        # 项目
    PRESENTATION = "presentation"  # 演讲
    PARTICIPATION = "participation"  # 课堂参与
    LAB = "lab"               # 实验课
    ATTENDANCE = "attendance"  # 出勤
    OTHER = "other"           # 其他

class Grade(BaseModel):
    """成绩模型"""

    __tablename__ = 'grades'

    # 关联信息
    student_id = Column(db.CHAR(36), db.ForeignKey('students.id'), nullable=False)
    course_id = Column(db.CHAR(36), db.ForeignKey('courses.id'), nullable=False)

    # 成绩信息
    exam_type = Column(Enum(GradeType), nullable=False)
    exam_name = Column(String(100))  # 考试名称，如：期中考试、期末考试、作业1等
    score = Column(Float)  # 成绩分数
    max_score = Column(Float, default=100.0)  # 满分

    # 权重和学期
    weight = Column(Float, default=1.0)  # 权重
    semester = Column(String(20), nullable=False)  # 学期

    # 评分信息
    graded_by = Column(db.CHAR(36), db.ForeignKey('users.id'), nullable=False)  # 评分教师
    graded_at = Column(DateTime, default=datetime.utcnow)  # 评分时间
    grading_method = Column(String(20), default='manual')  # manual, auto, curve

    # 分数调整
    original_score = Column(Float)  # 原始分数
    curve_points = Column(Float, default=0.0)  # 调整分数
    curve_reason = Column(Text)  # 调整原因

    # 统计信息
    class_average = Column(Float)  # 班级平均分
    class_max = Column(Float)  # 班级最高分
    class_min = Column(Float)  # 班级最低分
    percentile = Column(Float)  # 百分位

    # 状态信息
    is_published = Column(db.Boolean, default=False)  # 是否已发布
    published_at = Column(DateTime)  # 发布时间
    is_locked = Column(db.Boolean, default=False)  # 是否锁定
    locked_at = Column(DateTime)  # 锁定时间

    # 补考信息
    is_makeup = Column(db.Boolean, default=False)  # 是否为补考
    makeup_reason = Column(Text)  # 补考原因
    makeup_date = Column(DateTime)  # 补考时间

    # 评分细则
    rubric_scores = Column(db.JSON)  # 评分细则分数
    rubric_comments = Column(db.JSON)  # 评分细则评语

    # 评语和反馈
    comments = Column(Text)  # 教师评语
    student_feedback = Column(Text)  # 学生反馈
    improvement_suggestions = Column(Text)  # 改进建议

    # 附加信息
    submission_file = Column(String(255))  # 提交文件路径
    submission_date = Column(DateTime)  # 提交时间
    late_submission = Column(db.Boolean, default=False)  # 是否迟交
    late_penalty = Column(Float, default=0.0)  # 迟交扣分

    # 关系
    student = relationship("Student", back_populates="grades")
    course = relationship("Course", back_populates="grades")
    grader = relationship("User", foreign_keys=[graded_by])

    # 索引和约束
    __table_args__ = (
        Index('idx_student_course_type', 'student_id', 'course_id', 'exam_type'),
        Index('idx_course_semester_type', 'course_id', 'semester', 'exam_type'),
        Index('idx_graded_by_date', 'graded_by', 'graded_at'),
        Index('idx_exam_name', 'exam_name'),
        CheckConstraint('score >= 0 AND score <= max_score', name='check_score_range'),
        CheckConstraint('max_score > 0', name='check_max_score_positive'),
        CheckConstraint('weight >= 0', name='check_weight_positive'),
        CheckConstraint('curve_points >= 0', name='check_curve_points_positive'),
    )

    def __init__(self, **kwargs):
        super(Grade, self).__init__(**kwargs)
        if not self.graded_at:
            self.graded_at = datetime.utcnow()

    @property
    def display_type(self):
        """获取成绩类型显示名称"""
        type_mapping = {
            GradeType.QUIZ: "测验",
            GradeType.ASSIGNMENT: "作业",
            GradeType.MIDTERM: "期中考试",
            GradeType.FINAL: "期末考试",
            GradeType.PROJECT: "项目",
            GradeType.PRESENTATION: "演讲",
            GradeType.PARTICIPATION: "课堂参与",
            GradeType.LAB: "实验课",
            GradeType.ATTENDANCE: "出勤",
            GradeType.OTHER: "其他"
        }
        return type_mapping.get(self.exam_type, "成绩")

    @property
    def percentage(self):
        """获取百分比分数"""
        if self.max_score and self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0

    @property
    def letter_grade(self):
        """获取等级成绩"""
        if self.score is None:
            return None

        percentage = self.percentage
        if percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "A-"
        elif percentage >= 82:
            return "B+"
        elif percentage >= 78:
            return "B"
        elif percentage >= 75:
            return "B-"
        elif percentage >= 72:
            return "C+"
        elif percentage >= 68:
            return "C"
        elif percentage >= 64:
            return "C-"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    @property
    def grade_point(self):
        """获取绩点"""
        if self.score is None:
            return None

        percentage = self.percentage
        if percentage >= 90:
            return 4.0
        elif percentage >= 85:
            return 3.7
        elif percentage >= 82:
            return 3.3
        elif percentage >= 78:
            return 3.0
        elif percentage >= 75:
            return 2.7
        elif percentage >= 72:
            return 2.3
        elif percentage >= 68:
            return 2.0
        elif percentage >= 64:
            return 1.5
        elif percentage >= 60:
            return 1.0
        else:
            return 0.0

    @property
    def is_passing(self):
        """是否及格"""
        if self.score is None:
            return False
        return self.percentage >= 60

    @property
    def can_be_modified(self):
        """是否可以修改"""
        return not self.is_locked

    @property
    def display_score(self):
        """获取显示分数"""
        if self.score is None:
            return "未评分"
        return f"{self.score:.1f}/{self.max_score} ({self.percentage:.1f}%)"

    def apply_curve(self, curve_points, reason):
        """应用分数调整"""
        self.original_score = self.score
        self.curve_points = curve_points
        self.curve_reason = reason
        self.score = min(self.max_score, self.score + curve_points)
        self.save()

    def remove_curve(self):
        """移除分数调整"""
        if self.original_score is not None:
            self.score = self.original_score
            self.original_score = None
            self.curve_points = 0
            self.curve_reason = None
            self.save()

    def publish(self):
        """发布成绩"""
        self.is_published = True
        self.published_at = datetime.utcnow()
        self.save()

    def unpublish(self):
        """取消发布成绩"""
        self.is_published = False
        self.published_at = None
        self.save()

    def lock(self):
        """锁定成绩"""
        self.is_locked = True
        self.locked_at = datetime.utcnow()
        self.save()

    def unlock(self):
        """解锁成绩"""
        self.is_locked = False
        self.locked_at = None
        self.save()

    def add_comment(self, comment):
        """添加评语"""
        if self.comments:
            self.comments += f"\n\n{comment}"
        else:
            self.comments = comment
        self.save()

    def update_score(self, new_score, grader_id, reason=None):
        """更新分数"""
        if self.is_locked:
            raise ValueError("成绩已锁定，无法修改")

        self.score = new_score
        self.graded_by = grader_id
        self.graded_at = datetime.utcnow()

        if reason:
            if self.comments:
                self.comments += f"\n\n修改原因: {reason}"
            else:
                self.comments = f"修改原因: {reason}"

        self.save()

    def calculate_class_statistics(self):
        """计算班级统计信息"""
        # 获取同一课程、同类型考试的所有成绩
        same_exams = Grade.query.filter_by(
            course_id=self.course_id,
            exam_type=self.exam_type,
            exam_name=self.exam_name,
            semester=self.semester
        ).filter(Grade.score.isnot(None)).all()

        if not same_exams:
            return

        scores = [grade.score for grade in same_exams]
        self.class_average = sum(scores) / len(scores)
        self.class_max = max(scores)
        self.class_min = min(scores)

        # 计算百分位
        scores_sorted = sorted(scores)
        rank = scores_sorted.index(self.score) + 1
        self.percentile = (rank / len(scores_sorted)) * 100

        # 更新所有相同考试的成绩统计
        for grade in same_exams:
            grade.class_average = self.class_average
            grade.class_max = self.class_max
            grade.class_min = self.class_min
            db.session.add(grade)

        db.session.commit()

    def get_student_rank(self):
        """获取学生排名"""
        if self.score is None:
            return None

        same_exams = Grade.query.filter_by(
            course_id=self.course_id,
            exam_type=self.exam_type,
            exam_name=self.exam_name,
            semester=self.semester
        ).filter(Grade.score.isnot(None)).order_by(Grade.score.desc()).all()

        for rank, grade in enumerate(same_exams, 1):
            if grade.id == self.id:
                return rank

        return None

    def get_rubric_summary(self):
        """获取评分细则摘要"""
        if not self.rubric_scores:
            return None

        summary = {}
        for criterion, score in self.rubric_scores.items():
            summary[criterion] = {
                'score': score,
                'comment': self.rubric_comments.get(criterion, '') if self.rubric_comments else ''
            }

        return summary

    def add_rubric_score(self, criterion, score, comment=""):
        """添加评分细则分数"""
        if not self.rubric_scores:
            self.rubric_scores = {}
        if not self.rubric_comments:
            self.rubric_comments = {}

        self.rubric_scores[criterion] = score
        self.rubric_comments[criterion] = comment
        self.save()

    def get_grade_trend(self):
        """获取成绩趋势（同类型考试的多次成绩）"""
        grades = Grade.query.filter_by(
            student_id=self.student_id,
            course_id=self.course_id,
            exam_type=self.exam_type
        ).order_by(Grade.created_at).all()

        return [{"date": grade.created_at.isoformat(), "score": grade.score} for grade in grades]

    def to_dict(self, include_student=True, include_course=True, include_grader=True):
        """转换为字典"""
        data = super().to_dict()
        data['display_type'] = self.display_type
        data['display_score'] = self.display_score
        data['percentage'] = self.percentage
        data['letter_grade'] = self.letter_grade
        data['grade_point'] = self.grade_point
        data['is_passing'] = self.is_passing

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
                'credits': self.course.credits
            }

        if include_grader and self.grader:
            data['grader'] = {
                'id': self.grader.id,
                'name': self.grader.profile.full_name if self.grader.profile else self.grader.username
            }

        return data

    @classmethod
    def get_student_grades(cls, student_id, course_id=None, semester=None):
        """获取学生成绩"""
        query = cls.query.filter_by(student_id=student_id)

        if course_id:
            query = query.filter_by(course_id=course_id)
        if semester:
            query = query.filter_by(semester=semester)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_course_grades(cls, course_id, exam_type=None, semester=None):
        """获取课程成绩"""
        query = cls.query.filter_by(course_id=course_id)

        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        if semester:
            query = query.filter_by(semester=semester)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unpublished_grades(cls, course_id=None):
        """获取未发布的成绩"""
        query = cls.query.filter_by(is_published=False)

        if course_id:
            query = query.filter_by(course_id=course_id)

        return query.order_by(cls.created_at.asc()).all()

    def __repr__(self):
        return f"<Grade(student='{self.student.student_id if self.student else 'Unknown'}', course='{self.course.course_code if self.course else 'Unknown'}', type='{self.exam_type.value}', score={self.score})>"