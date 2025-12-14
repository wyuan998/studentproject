# ========================================
# 学生信息管理系统 - 用户序列化模式
# ========================================

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from extensions import ma
from models import User, UserProfile, UserRole, UserStatus

class BaseSchema(SQLAlchemyAutoSchema):
    """基础序列化模式"""

    class Meta:
        sqla_session = ma.session
        load_instance = True
        include_fk = True

class UserProfileSchema(BaseSchema):
    """用户资料序列化模式"""

    class Meta(BaseSchema.Meta):
        model = UserProfile
        include_fk = True
        exclude = ('user',)  # 排除反向关系

    # 自定义字段
    full_name = fields.Method('get_full_name')
    display_phone = fields.Method('get_display_phone')
    age = fields.Method('get_age')

    def get_full_name(self, obj):
        """获取全名"""
        if obj:
            return f"{obj.first_name} {obj.last_name}"
        return ""

    def get_display_phone(self, obj):
        """获取显示电话（隐藏部分数字）"""
        if obj and obj.phone and len(obj.phone) >= 7:
            return f"{obj.phone[:3]}****{obj.phone[-4:]}"
        return ""

    def get_age(self, obj):
        """计算年龄"""
        if obj and obj.birthday:
            from datetime import date
            today = date.today()
            return today.year - obj.birthday.year - (
                (today.month, today.day) < (obj.birthday.month, obj.birthday.day)
            )
        return None

class UserSchema(BaseSchema):
    """用户序列化模式"""

    class Meta(BaseSchema.Meta):
        model = User
        exclude = ('password_hash',)  # 排除密码哈希

    # 关联字段
    profile = fields.Nested(UserProfileSchema, exclude=('user',))

    # 自定义字段
    display_name = fields.Method('get_display_name')
    display_role = fields.Method('get_display_role')
    display_status = fields.Method('get_display_status')
    is_active = fields.Method('get_is_active')
    is_locked = fields.Method('get_is_locked')

    def get_display_name(self, obj):
        """获取显示名称"""
        if obj.profile:
            return f"{obj.profile.first_name} {obj.profile.last_name}"
        return obj.username

    def get_display_role(self, obj):
        """获取角色显示名称"""
        role_mapping = {
            UserRole.ADMIN: "管理员",
            UserRole.TEACHER: "教师",
            UserRole.STUDENT: "学生"
        }
        return role_mapping.get(obj.role, "未知")

    def get_display_status(self, obj):
        """获取状态显示名称"""
        status_mapping = {
            UserStatus.ACTIVE: "激活",
            UserStatus.INACTIVE: "未激活",
            UserStatus.SUSPENDED: "暂停"
        }
        return status_mapping.get(obj.status, "未知")

    def get_is_active(self, obj):
        """检查是否激活"""
        return obj.is_active()

    def get_is_locked(self, obj):
        """检查是否锁定"""
        return obj.is_locked()

class UserCreateSchema(Schema):
    """用户创建模式"""

    # 基本信息
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
        validate=validate.Length(min=6, max=128, error="密码长度必须在6-128位之间"),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        load_only=True
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(['admin', 'teacher', 'student'], error="角色必须是admin、teacher或student")
    )
    status = fields.Str(
        missing='active',
        validate=validate.OneOf(['active', 'inactive', 'suspended'], error="状态必须是active、inactive或suspended")
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
        validate=validate.OneOf(['male', 'female', 'other'], error="性别必须是male、female或other"),
        allow_none=True
    )
    birthday = fields.Date(allow_none=True)

    @validates('username')
    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.query.filter_by(username=value).first():
            raise ValidationError("用户名已存在")

    @validates('email')
    def validate_email(self, value):
        """验证邮箱唯一性"""
        if User.query.filter_by(email=value).first():
            raise ValidationError("邮箱已存在")

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("密码确认不匹配", field_name='confirm_password')

class UserUpdateSchema(Schema):
    """用户更新模式"""

    # 基本信息（可选）
    email = fields.Email(
        validate=validate.Length(max=100),
        allow_none=True
    )
    role = fields.Str(
        validate=validate.OneOf(['admin', 'teacher', 'student']),
        allow_none=True
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'suspended']),
        allow_none=True
    )
    password = fields.Str(
        validate=validate.Length(min=6, max=128),
        load_only=True,
        allow_none=True
    )
    confirm_password = fields.Str(
        load_only=True,
        allow_none=True
    )

    # 用户资料
    first_name = fields.Str(
        validate=validate.Length(min=1, max=50),
        allow_none=True
    )
    last_name = fields.Str(
        validate=validate.Length(min=1, max=50),
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
    major = fields.Str(allow_none=True)
    degree = fields.Str(allow_none=True)

    @validates('email')
    def validate_email(self, value):
        """验证邮箱唯一性（排除自己）"""
        if value:
            from flask import g
            user_id = g.current_user.id if hasattr(g, 'current_user') else None
            existing = User.query.filter_by(email=value).first()
            if existing and existing.id != user_id:
                raise ValidationError("邮箱已被其他用户使用")

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password and password != confirm_password:
            raise ValidationError("密码确认不匹配", field_name='confirm_password')

class UserLoginSchema(Schema):
    """用户登录模式"""

    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    remember_me = fields.Boolean(missing=False)

class UserPasswordChangeSchema(Schema):
    """密码修改模式"""

    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True
    )
    confirm_password = fields.Str(required=True, load_only=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError("新密码确认不匹配", field_name='confirm_password')

class UserPasswordResetSchema(Schema):
    """密码重置模式"""

    email = fields.Email(required=True)

class UserRegisterSchema(Schema):
    """用户注册模式"""

    # 基本信息
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
        validate=validate.And(
            validate.Length(min=6, max=128, error="密码长度必须在6-128位之间"),
            validate.Regexp(r'^(?=.*[a-z])(?=.*\d)', error="密码必须包含字母和数字")
        ),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        load_only=True
    )
    phone = fields.Str(
        required=True,
        validate=validate.Regexp(r'^1[3-9]\d{9}$', error="请输入有效的手机号码")
    )
    real_name = fields.Str(
        required=True,
        validate=validate.And(
            validate.Length(min=2, max=10, error="姓名长度为2-10位"),
            validate.Regexp(r'^[\u4e00-\u9fa5]+$', error="姓名必须为中文")
        )
    )
    student_id = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{10,12}$', error="学生号应为10-12位数字")
    )
    captcha = fields.Str(
        required=True,
        validate=validate.Length(min=4, max=4, error="验证码长度为4位"),
        load_only=True
    )

    @validates('username')
    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.query.filter_by(username=value).first():
            raise ValidationError("用户名已存在")

    @validates('email')
    def validate_email(self, value):
        """验证邮箱唯一性"""
        if User.query.filter_by(email=value).first():
            raise ValidationError("邮箱已被注册")

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("密码确认不匹配", field_name='confirm_password')

class UserProfileSimpleSchema(BaseSchema):
    """简单用户资料模式（用于嵌套显示）"""

    class Meta(BaseSchema.Meta):
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone', 'department')

class UserSimpleSchema(BaseSchema):
    """简单用户模式（用于嵌套显示）"""

    class Meta(BaseSchema.Meta):
        model = User
        fields = ('id', 'username', 'email', 'role')

    profile = fields.Nested(UserProfileSimpleSchema)

class UserListSchema(Schema):
    """用户列表模式"""

    users = fields.List(fields.Nested(UserSimpleSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()

class UserSearchSchema(Schema):
    """用户搜索模式"""

    keyword = fields.Str(allow_none=True)
    role = fields.Str(
        validate=validate.OneOf(['admin', 'teacher', 'student', '']),
        allow_none=True
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'suspended', '']),
        allow_none=True
    )
    department = fields.Str(allow_none=True)
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        missing='created_at',
        validate=validate.OneOf(['username', 'email', 'role', 'status', 'created_at'])
    )
    sort_order = fields.Str(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )