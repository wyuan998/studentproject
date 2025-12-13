# ========================================
# 学生信息管理系统 - 学生序列化模式
# ========================================

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from datetime import datetime
from extensions import ma
from models import Student, AcademicStatus
from .user import UserSimpleSchema

class BaseSchema(SQLAlchemyAutoSchema):
    """基础序列化模式"""

    class Meta:
        sqla_session = ma.session
        load_instance = True
        include_fk = True

class StudentSchema(BaseSchema):
    """学生序列化模式"""

    class Meta(BaseSchema.Meta):
        model = Student
        include_fk = True

    # 关联字段
    user = fields.Nested(UserSimpleSchema)
    advisor = fields.Nested('schemas.teacher.TeacherSimpleSchema', allow_none=True)

    # 自定义字段
    full_student_id = fields.Method('get_full_student_id')
    class_display = fields.Method('get_class_display')
    display_status = fields.Method('get_display_status')
    is_active = fields.Method('get_is_active')
    academic_progress = fields.Method('get_academic_progress')
    current_courses_count = fields.Method('get_current_courses_count')
    honors = fields.Method('get_honors')

    def get_full_student_id(self, obj):
        """获取完整学号"""
        if obj:
            return obj.full_student_id
        return ""

    def get_class_display(self, obj):
        """获取班级显示名称"""
        if obj:
            return obj.class_display
        return ""

    def get_display_status(self, obj):
        """获取学业状态显示名称"""
        if obj and obj.academic_status:
            status_mapping = {
                AcademicStatus.ENROLLED: "在读",
                AcademicStatus.GRADUATED: "已毕业",
                AcademicStatus.SUSPENDED: "暂停",
                AcademicStatus.WITHDRAWN: "退学",
                AcademicStatus.ON_LEAVE: "休学"
            }
            return status_mapping.get(obj.academic_status, "未知")
        return ""

    def get_is_active(self, obj):
        """是否在读"""
        if obj:
            return obj.is_active
        return False

    def get_academic_progress(self, obj):
        """学业进度"""
        if obj:
            return obj.academic_progress
        return 0

    def get_current_courses_count(self, obj):
        """当前课程数量"""
        if obj:
            return len(obj.get_current_semester_courses())
        return 0

    def get_honors(self, obj):
        """荣誉信息"""
        if obj:
            return obj.get_honors()
        return []

class StudentCreateSchema(Schema):
    """学生创建模式"""

    # 基本信息
    student_id = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{4,20}$', error="学号必须是4-20位数字")
    )
    grade = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{4}$', error="年级必须是4位数字")
    )
    class_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    major = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    minor = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100)
    )

    # 学业信息
    enrollment_date = fields.Date(required=True)
    expected_graduation_date = fields.Date(allow_none=True)
    academic_status = fields.Str(
        missing='enrolled',
        validate=validate.OneOf(['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave'])
    )

    # 绩点信息
    gpa = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0.0, max=4.0, error="GPA必须在0.0-4.0之间")
    )
    credits_earned = fields.Integer(
        missing=0,
        validate=validate.Range(min=0, error="已修学分不能为负数")
    )
    credits_in_progress = fields.Integer(
        missing=0,
        validate=validate.Range(min=0, error="在修学分不能为负数")
    )

    # 辅导员
    advisor_id = fields.Str(
        allow_none=True,
        validate=validate.UUID(error="辅导员ID格式不正确")
    )

    # 其他信息
    notes = fields.Str(allow_none=True)
    tags = fields.List(fields.Str(), missing=[])

    # 用户信息
    username = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[a-zA-Z0-9_]{3,20}$', error="用户名必须是3-20位字母、数字或下划线")
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=100)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        load_only=True
    )

    # 用户资料
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    phone = fields.Str(
        validate=validate.Regexp(r'^1[3-9]\d{9}$', error="请输入有效的手机号码"),
        allow_none=True
    )
    gender = fields.Str(
        validate=validate.OneOf(['male', 'female', 'other']),
        allow_none=True
    )
    birthday = fields.Date(allow_none=True)
    address = fields.Str(allow_none=True)

    @validates('student_id')
    def validate_student_id(self, value):
        """验证学号唯一性"""
        if Student.query.filter_by(student_id=value).first():
            raise ValidationError("学号已存在")

    @validates('username')
    def validate_username(self, value):
        """验证用户名唯一性"""
        from models import User
        if User.query.filter_by(username=value).first():
            raise ValidationError("用户名已存在")

    @validates('email')
    def validate_email(self, value):
        """验证邮箱唯一性"""
        from models import User
        if User.query.filter_by(email=value).first():
            raise ValidationError("邮箱已存在")

    @validates('advisor_id')
    def validate_advisor(self, value):
        """验证辅导员是否存在且为教师"""
        from models import Teacher
        if value:
            advisor = Teacher.query.filter_by(id=value).first()
            if not advisor:
                raise ValidationError("指定的辅导员不存在")

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("密码确认不匹配", field_name='confirm_password')

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """验证日期逻辑"""
        enrollment_date = data.get('enrollment_date')
        expected_graduation_date = data.get('expected_graduation_date')
        grade = data.get('grade', '')

        if enrollment_date and expected_graduation_date:
            if expected_graduation_date <= enrollment_date:
                raise ValidationError("预计毕业日期必须晚于入学日期", field_name='expected_graduation_date')

        # 验证年级与入学日期的一致性
        if enrollment_date and grade:
            enrollment_year = str(enrollment_date.year)
            if enrollment_year != grade:
                raise ValidationError("年级与入学年份不一致", field_name='grade')

class StudentUpdateSchema(Schema):
    """学生更新模式"""

    # 基本信息
    grade = fields.Str(
        validate=validate.Regexp(r'^\d{4}$', error="年级必须是4位数字"),
        allow_none=True
    )
    class_name = fields.Str(
        validate=validate.Length(min=1, max=50),
        allow_none=True
    )
    major = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True
    )
    minor = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True
    )

    # 学业信息
    expected_graduation_date = fields.Date(allow_none=True)
    academic_status = fields.Str(
        validate=validate.OneOf(['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave']),
        allow_none=True
    )

    # 绩点信息
    gpa = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0.0, max=4.0)
    )
    credits_earned = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=0)
    )
    credits_in_progress = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=0)
    )

    # 辅导员
    advisor_id = fields.Str(
        allow_none=True,
        validate=validate.UUID(error="辅导员ID格式不正确")
    )

    # 其他信息
    notes = fields.Str(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)

    # 用户资料
    email = fields.Email(
        validate=validate.Length(max=100),
        allow_none=True
    )
    phone = fields.Str(
        validate=validate.Regexp(r'^1[3-9]\d{9}$'),
        allow_none=True
    )
    gender = fields.Str(
        validate=validate.OneOf(['male', 'female', 'other']),
        allow_none=True
    )
    birthday = fields.Date(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    province = fields.Str(allow_none=True)
    postal_code = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    department = fields.Str(allow_none=True)

    @validates('advisor_id')
    def validate_advisor(self, value):
        """验证辅导员是否存在且为教师"""
        from models import Teacher
        if value:
            advisor = Teacher.query.filter_by(id=value).first()
            if not advisor:
                raise ValidationError("指定的辅导员不存在")

    @validates('email')
    def validate_email(self, value):
        """验证邮箱唯一性（排除自己）"""
        from models import User
        from flask import g
        if value and hasattr(g, 'current_user'):
            current_student = Student.query.filter_by(user_id=g.current_user.id).first()
            if current_student:
                existing = User.query.filter_by(email=value).first()
                if existing and existing.id != current_student.user_id:
                    raise ValidationError("邮箱已被其他用户使用")

class StudentSimpleSchema(BaseSchema):
    """简单学生模式（用于嵌套显示）"""

    class Meta(BaseSchema.Meta):
        model = Student
        fields = ('id', 'student_id', 'grade', 'class_name', 'major', 'academic_status')

    user = fields.Nested('schemas.user.UserSimpleSchema')

class StudentSearchSchema(Schema):
    """学生搜索模式"""

    # 搜索条件
    keyword = fields.Str(allow_none=True)  # 搜索学号、姓名等
    student_id = fields.Str(allow_none=True)
    grade = fields.Str(allow_none=True)
    class_name = fields.Str(allow_none=True)
    major = fields.Str(allow_none=True)
    academic_status = fields.Str(
        validate=validate.OneOf(['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave', '']),
        allow_none=True
    )
    advisor_id = fields.Str(validate=validate.UUID(error="辅导员ID格式不正确"), allow_none=True)
    department = fields.Str(allow_none=True)

    # GPA范围
    gpa_min = fields.Float(validate=validate.Range(min=0.0, max=4.0), allow_none=True)
    gpa_max = fields.Float(validate=validate.Range(min=0.0, max=4.0), allow_none=True)

    # 学分范围
    credits_min = fields.Integer(validate=validate.Range(min=0), allow_none=True)
    credits_max = fields.Integer(validate=validate.Range(min=0), allow_none=True)

    # 入学时间范围
    enrollment_start = fields.Date(allow_none=True)
    enrollment_end = fields.Date(allow_none=True)

    # 标签
    tags = fields.List(fields.Str(), allow_none=True)

    # 分页和排序
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        missing='student_id',
        validate=validate.OneOf(['student_id', 'grade', 'class_name', 'major', 'gpa', 'credits_earned', 'enrollment_date'])
    )
    sort_order = fields.Str(
        missing='asc',
        validate=validate.OneOf(['asc', 'desc'])
    )

class StudentBulkActionSchema(Schema):
    """学生批量操作模式"""

    student_ids = fields.List(
        fields.Str(validate=validate.UUID(error="学生ID格式不正确")),
        required=True,
        validate=validate.Length(min=1, error="请至少选择一个学生")
    )
    action = fields.Str(
        required=True,
        validate=validate.OneOf(['activate', 'deactivate', 'suspend', 'graduate', 'add_tag', 'remove_tag'], error="操作类型无效")
    )
    action_data = fields.Dict(allow_none=True)  # 操作所需的额外数据

class StudentStatsSchema(Schema):
    """学生统计模式"""

    total_students = fields.Int()
    active_students = fields.Int()
    graduated_students = fields.Int()
    suspended_students = fields.Int()
    on_leave_students = fields.Int()
    students_by_grade = fields.Dict()
    students_by_major = fields.Dict()
    average_gpa = fields.Float()
    gpa_distribution = fields.Dict()
    credit_distribution = fields.Dict()

class StudentImportSchema(Schema):
    """学生导入模式"""

    file = fields.Raw(required=True)  # 文件对象
    has_header = fields.Boolean(missing=True)
    encoding = fields.Str(missing='utf-8')
    overwrite_existing = fields.Boolean(missing=False)

class StudentExportSchema(Schema):
    """学生导出模式"""

    # 筛选条件
    grade = fields.Str(allow_none=True)
    major = fields.Str(allow_none=True)
    academic_status = fields.Str(
        validate=validate.OneOf(['enrolled', 'graduated', 'suspended', 'withdrawn', 'on_leave']),
        allow_none=True
    )
    advisor_id = fields.Str(validate=validate.UUID(error="辅导员ID格式不正确"), allow_none=True)

    # 导出选项
    format = fields.Str(
        missing='excel',
        validate=validate.OneOf(['excel', 'csv', 'json'])
    )
    include_profile = fields.Boolean(missing=True)
    include_academic = fields.Boolean(missing=True)
    include_contact = fields.Boolean(missing=True)

class StudentGraduationSchema(Schema):
    """学生毕业模式"""

    graduation_date = fields.Date(required=True)
    final_gpa = fields.Float(
        required=True,
        validate=validate.Range(min=0.0, max=4.0)
    )
    final_credits = fields.Integer(
        required=True,
        validate=validate.Range(min=0)
    )
    honors = fields.List(fields.Str(), allow_none=True)
    notes = fields.Str(allow_none=True)