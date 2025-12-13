# ========================================
# 学生信息管理系统 - 消息模板序列化模式（独立文件）
# ========================================

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from extensions import ma
from models import MessageTemplate, MessageType
from .user import UserSimpleSchema

class BaseSchema(SQLAlchemyAutoSchema):
    """基础序列化模式"""

    class Meta:
        sqla_session = ma.session
        load_instance = True
        include_fk = True

class MessageTemplateSchema(BaseSchema):
    """消息模板序列化模式"""

    class Meta(BaseSchema.Meta):
        model = MessageTemplate
        include_fk = True

    # 关联字段
    creator = fields.Nested(UserSimpleSchema, exclude=('email',), allow_none=True)
    updater = fields.Nested(UserSimpleSchema, exclude=('email',), allow_none=True)

    # 自定义字段
    display_type = fields.Method('get_display_type')
    variables_preview = fields.Method('get_variables_preview')
    is_frequently_used = fields.Method('get_is_frequently_used')
    last_used_ago = fields.Method('get_last_used_ago')

    def get_display_type(self, obj):
        """获取模板类型显示名称"""
        if obj and obj.type:
            type_mapping = {
                MessageType.SYSTEM: "系统通知",
                MessageType.BUSINESS: "业务通知",
                MessageType.NOTIFICATION: "通知消息",
                MessageType.ANNOUNCEMENT: "公告",
                MessageType.REMINDER: "提醒",
                MessageType.WARNING: "警告",
                MessageType.ERROR: "错误",
                MessageType.SUCCESS: "成功"
            }
            return type_mapping.get(obj.type, "消息")
        return ""

    def get_variables_preview(self, obj):
        """获取变量预览"""
        if obj and obj.variables:
            return list(obj.variables.keys())[:5]  # 只显示前5个变量
        return []

    def get_is_frequently_used(self, obj):
        """是否为常用模板"""
        if obj and obj.usage_count:
            return obj.usage_count >= 10  # 使用次数超过10次认为是常用
        return False

    def get_last_used_ago(self, obj):
        """最后使用时间描述"""
        if obj and obj.last_used_at:
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            diff = now - obj.last_used_at

            if diff.days > 0:
                return f"{diff.days}天前"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}小时前"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}分钟前"
            else:
                return "刚刚"
        return "从未使用"

class MessageTemplateCreateSchema(Schema):
    """消息模板创建模式"""

    # 基本信息
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="模板名称长度必须在1-100字符之间")
    )
    title_template = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error="标题模板长度必须在1-200字符之间")
    )
    content_template = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000, error="内容模板长度必须在1-5000字符之间")
    )

    # 分类信息
    type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success'],
            error="模板类型无效"
        )
    )
    category = fields.Str(allow_none=True, validate=validate.Length(max=50))

    # 模板变量
    variables = fields.Dict(allow_none=True)
    default_variables = fields.Dict(allow_none=True)

    # 状态
    is_active = fields.Boolean(missing=True)
    is_system = fields.Boolean(missing=False)

    @validates('name')
    def validate_name(self, value):
        """验证模板名称唯一性"""
        if MessageTemplate.query.filter_by(name=value).first():
            raise ValidationError("模板名称已存在")

    @validates_schema
    def validate_templates(self, data, **kwargs):
        """验证模板格式"""
        title_template = data.get('title_template')
        content_template = data.get('content_template')
        variables = data.get('variables', {})

        # 检查模板中的变量是否在变量列表中定义
        import re

        if title_template:
            title_vars = re.findall(r'\{(\w+)\}', title_template)
            for var in title_vars:
                if var not in variables:
                    raise ValidationError(f"标题模板中的变量 '{var}' 未在变量列表中定义")

        if content_template:
            content_vars = re.findall(r'\{(\w+)\}', content_template)
            for var in content_vars:
                if var not in variables:
                    raise ValidationError(f"内容模板中的变量 '{var}' 未在变量列表中定义")

        # 验证变量格式
        if variables:
            for var_name, var_desc in variables.items():
                if not isinstance(var_name, str) or not var_name.isidentifier():
                    raise ValidationError(f"变量名 '{var_name}' 格式无效，必须是有效的Python标识符")

class MessageTemplateUpdateSchema(MessageTemplateCreateSchema):
    """消息模板更新模式"""

    # 允许更新所有创建模式的字段
    name = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True
    )
    title_template = fields.Str(
        validate=validate.Length(min=1, max=200),
        allow_none=True
    )
    content_template = fields.Str(
        validate=validate.Length(min=1, max=5000),
        allow_none=True
    )
    type = fields.Str(
        validate=validate.OneOf(
            ['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']
        ),
        allow_none=True
    )
    category = fields.Str(allow_none=True, validate=validate.Length(max=50))
    variables = fields.Dict(allow_none=True)
    default_variables = fields.Dict(allow_none=True)
    is_active = fields.Boolean(allow_none=True)
    is_system = fields.Boolean(allow_none=True)

    # 重写name验证，允许更新时使用相同名称
    @validates('name')
    def validate_name(self, value):
        """验证模板名称唯一性（排除自己）"""
        from flask import g
        template_id = getattr(g, 'template_id', None)
        existing = MessageTemplate.query.filter_by(name=value).first()
        if existing and existing.id != template_id:
            raise ValidationError("模板名称已被其他模板使用")

class MessageTemplatePreviewSchema(Schema):
    """消息模板预览模式"""

    variables = fields.Dict(required=True)
    sample_data = fields.Dict(missing={})

    @validates_schema
    def validate_preview_data(self, data, **kwargs):
        """验证预览数据"""
        variables = data.get('variables', {})
        sample_data = data.get('sample_data', {})

        # 检查是否所有需要的变量都有值
        for var_name in variables.keys():
            if var_name not in sample_data:
                # 使用默认值或占位符
                sample_data[var_name] = f"[{variables[var_name]}]"

        data['sample_data'] = sample_data

class MessageTemplateDuplicateSchema(Schema):
    """消息模板复制模式"""

    new_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    new_category = fields.Str(
        allow_none=True,
        validate=validate.Length(max=50)
    )
    copy_variables = fields.Boolean(missing=True)
    copy_default_values = fields.Boolean(missing=True)

class MessageTemplateSearchSchema(Schema):
    """消息模板搜索模式"""

    # 搜索条件
    keyword = fields.Str(allow_none=True)
    type = fields.Str(
        validate=validate.OneOf(['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success', '']),
        allow_none=True
    )
    category = fields.Str(allow_none=True)
    is_active = fields.Boolean(allow_none=True)
    is_system = fields.Boolean(allow_none=True)
    creator_id = fields.Str(validate=validate.UUID(error="创建者ID格式不正确"), allow_none=True)

    # 分页和排序
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        missing='created_at',
        validate=validate.OneOf(['name', 'type', 'category', 'usage_count', 'last_used_at', 'created_at'])
    )
    sort_order = fields.Str(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )

class MessageTemplateStatsSchema(Schema):
    """消息模板统计模式"""

    total_templates = fields.Int()
    active_templates = fields.Int()
    system_templates = fields.Int()
    user_templates = fields.Int()
    templates_by_type = fields.Dict()
    most_used_templates = fields.List(fields.Dict())
    recently_used_templates = fields.List(fields.Dict())

class MessageTemplateBulkActionSchema(Schema):
    """消息模板批量操作模式"""

    template_ids = fields.List(
        fields.Str(validate=validate.UUID(error="模板ID格式不正确")),
        required=True,
        validate=validate.Length(min=1, error="请至少选择一个模板")
    )
    action = fields.Str(
        required=True,
        validate=validate.OneOf(['activate', 'deactivate', 'delete'], error="操作类型无效")
    )

class MessageTemplateVariableSchema(Schema):
    """模板变量定义模式"""

    name = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[a-zA-Z_][a-zA-Z0-9_]*$', error="变量名必须是有效的Python标识符")
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    type = fields.Str(
        missing='string',
        validate=validate.OneOf(['string', 'number', 'boolean', 'date', 'email', 'url'])
    )
    required = fields.Boolean(missing=False)
    default_value = fields.Str(allow_none=True)
    example_value = fields.Str(allow_none=True)

class MessageTemplateTestSchema(Schema):
    """消息模板测试模式"""

    template_id = fields.Str(
        required=True,
        validate=validate.UUID(error="模板ID格式不正确")
    )
    test_variables = fields.Dict(required=True)

class MessageTemplateImportSchema(Schema):
    """消息模板导入模式"""

    templates = fields.List(
        fields.Dict(),
        required=True,
        validate=validate.Length(min=1, error="请至少提供一个模板")
    )
    overwrite_existing = fields.Boolean(missing=False)

class MessageTemplateExportSchema(Schema):
    """消息模板导出模式"""

    template_ids = fields.List(
        fields.Str(validate=validate.UUID(error="模板ID格式不正确")),
        allow_none=True
    )
    type = fields.Str(
        validate=validate.OneOf(['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']),
        allow_none=True
    )
    category = fields.Str(allow_none=True)
    include_inactive = fields.Boolean(missing=False)
    format = fields.Str(
        missing='json',
        validate=validate.OneOf(['json', 'excel', 'csv'])
    )