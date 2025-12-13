# ========================================
# 学生信息管理系统 - 消息序列化模式
# ========================================

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from datetime import datetime
from extensions import ma
from models import Message, MessageTemplate, MessageType, MessageStatus, MessagePriority
from .user import UserSimpleSchema

class BaseSchema(SQLAlchemyAutoSchema):
    """基础序列化模式"""

    class Meta:
        sqla_session = ma.session
        load_instance = True
        include_fk = True

class MessageSchema(BaseSchema):
    """消息序列化模式"""

    class Meta(BaseSchema.Meta):
        model = Message
        include_fk = True

    # 关联字段
    sender = fields.Nested(UserSimpleSchema, exclude=('email',))
    receiver = fields.Nested(UserSimpleSchema, exclude=('email',))

    # 自定义字段
    display_type = fields.Method('get_display_type')
    display_priority = fields.Method('get_display_priority')
    display_status = fields.Method('get_display_status')
    content_preview = fields.Method('get_content_preview')
    age_hours = fields.Method('get_age_hours')
    is_unread = fields.Method('get_is_unread')
    is_read = fields.Method('get_is_read')
    is_urgent = fields.Method('get_is_urgent')
    can_be_replied = fields.Method('get_can_be_replied')
    sent_at_formatted = fields.Method('get_sent_at_formatted')
    read_at_formatted = fields.Method('get_read_at_formatted')

    def get_display_type(self, obj):
        """获取消息类型显示名称"""
        return obj.display_type

    def get_display_priority(self, obj):
        """获取优先级显示名称"""
        return obj.display_priority

    def get_display_status(self, obj):
        """获取状态显示名称"""
        return obj.display_status

    def get_content_preview(self, obj):
        """获取内容预览"""
        if obj:
            return obj.get_content_preview()
        return ""

    def get_age_hours(self, obj):
        """获取消息年龄"""
        if obj:
            return obj.get_age_hours()
        return 0

    def get_is_unread(self, obj):
        """是否未读"""
        if obj:
            return obj.is_unread
        return False

    def get_is_read(self, obj):
        """是否已读"""
        if obj:
            return obj.is_read
        return False

    def get_is_urgent(self, obj):
        """是否为紧急消息"""
        if obj:
            return obj.is_urgent
        return False

    def get_can_be_replied(self, obj):
        """是否可以回复"""
        if obj:
            return obj.can_be_replied()
        return False

    def get_sent_at_formatted(self, obj):
        """格式化发送时间"""
        if obj and obj.sent_at:
            return obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def get_read_at_formatted(self, obj):
        """格式化阅读时间"""
        if obj and obj.read_at:
            return obj.read_at.strftime('%Y-%m-%d %H:%M:%S')
        return ""

class MessageCreateSchema(Schema):
    """消息创建模式"""

    # 基本信息
    receiver_id = fields.Str(required=True, validate=validate.UUID(error="接收者ID格式不正确"))
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error="标题长度必须在1-200字符之间")
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000, error="内容长度必须在1-5000字符之间")
    )

    # 分类信息
    type = fields.Str(
        missing='notification',
        validate=validate.OneOf(
            ['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success'],
            error="消息类型无效"
        )
    )
    priority = fields.Str(
        missing='normal',
        validate=validate.OneOf(
            ['low', 'normal', 'high', 'urgent'],
            error="优先级无效"
        )
    )

    # 发送选项
    delivery_method = fields.Str(
        missing='system',
        validate=validate.OneOf(
            ['system', 'email', 'sms', 'push', 'both'],
            error="发送方式无效"
        )
    )
    scheduled_at = fields.DateTime(allow_none=True)
    is_recurring = fields.Boolean(missing=False)

    # 关联信息
    related_entity_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    related_entity_id = fields.Str(allow_none=True, validate=validate.UUID(error="关联实体ID格式不正确"))
    related_action = fields.Str(allow_none=True, validate=validate.Length(max=50))

    # 附件
    attachments = fields.List(
        fields.Dict(),
        missing=[]
    )

    # 标签
    tags = fields.List(fields.Str(), missing=[])

    @validates('receiver_id')
    def validate_receiver(self, value):
        """验证接收者是否存在"""
        from models import User
        if not User.query.get(value):
            raise ValidationError("接收者不存在")

    @validates('scheduled_at')
    def validate_schedule_time(self, value):
        """验证计划发送时间"""
        if value and value <= datetime.utcnow():
            raise ValidationError("计划发送时间必须是未来时间")

class MessageUpdateSchema(Schema):
    """消息更新模式"""

    # 基本信息
    title = fields.Str(
        validate=validate.Length(min=1, max=200),
        allow_none=True
    )
    content = fields.Str(
        validate=validate.Length(min=1, max=5000),
        allow_none=True
    )

    # 分类信息
    type = fields.Str(
        validate=validate.OneOf(
            ['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']
        ),
        allow_none=True
    )
    priority = fields.Str(
        validate=validate.OneOf(['low', 'normal', 'high', 'urgent']),
        allow_none=True
    )

    # 状态
    status = fields.Str(
        validate=validate.OneOf(['unread', 'read', 'archived', 'deleted']),
        allow_none=True
    )

    # 关联信息
    related_entity_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    related_entity_id = fields.Str(allow_none=True, validate=validate.UUID(error="关联实体ID格式不正确"))
    related_action = fields.Str(allow_none=True, validate=validate.Length(max=50))

    # 附件和标签
    attachments = fields.List(fields.Dict(), allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)

    @validates_schema
    def validate_status_change(self, data, **kwargs):
        """验证状态变更"""
        status = data.get('status')
        if status:
            # 如果要删除消息，需要验证权限
            if status == 'deleted':
                from flask import g
                if not hasattr(g, 'current_user') or not g.current_user.has_permission('message_management'):
                    raise ValidationError("只有管理员可以删除消息", field_name='status')

class MessageStatusUpdateSchema(Schema):
    """消息状态更新模式"""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(['read', 'unread', 'archived'], error="状态无效")
    )

class MessageBulkActionSchema(Schema):
    """消息批量操作模式"""

    message_ids = fields.List(
        fields.Str(validate=validate.UUID(error="消息ID格式不正确")),
        required=True,
        validate=validate.Length(min=1, error="请至少选择一条消息")
    )
    action = fields.Str(
        required=True,
        validate=validate.OneOf(['mark_read', 'mark_unread', 'archive', 'delete'], error="操作类型无效")
    )

class MessageSearchSchema(Schema):
    """消息搜索模式"""

    # 搜索条件
    keyword = fields.Str(allow_none=True)
    type = fields.Str(
        validate=validate.OneOf(['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success', '']),
        allow_none=True
    )
    priority = fields.Str(
        validate=validate.OneOf(['low', 'normal', 'high', 'urgent', '']),
        allow_none=True
    )
    status = fields.Str(
        validate=validate.OneOf(['unread', 'read', 'archived', 'deleted', '']),
        allow_none=True
    )
    sender_id = fields.Str(validate=validate.UUID(error="发送者ID格式不正确"), allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)

    # 分页和排序
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        missing='sent_at',
        validate=validate.OneOf(['sent_at', 'priority', 'type', 'status'])
    )
    sort_order = fields.Str(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )

class MessageSendSchema(Schema):
    """消息发送模式"""

    # 接收者（支持单个或批量）
    receiver_ids = fields.List(
        fields.Str(validate=validate.UUID(error="接收者ID格式不正确")),
        required=True,
        validate=validate.Length(min=1, error="请至少选择一个接收者")
    )
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )

    # 发送选项
    type = fields.Str(
        missing='notification',
        validate=validate.OneOf(['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success'])
    )
    priority = fields.Str(
        missing='normal',
        validate=validate.OneOf(['low', 'normal', 'high', 'urgent'])
    )
    delivery_method = fields.Str(
        missing='system',
        validate=validate.OneOf(['system', 'email', 'sms', 'push', 'both'])
    )

    # 定时发送
    scheduled_at = fields.DateTime(allow_none=True)
    is_recurring = fields.Boolean(missing=False)
    recurring_pattern = fields.Dict(allow_none=True)

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

class MessageTemplateUpdateSchema(MessageTemplateCreateSchema):
    """消息模板更新模式"""

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

class MessageListSchema(Schema):
    """消息列表模式"""

    messages = fields.List(fields.Nested(MessageSchema))
    total = fields.Int()
    unread_count = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()

class MessageStatsSchema(Schema):
    """消息统计模式"""

    total_messages = fields.Int()
    unread_messages = fields.Int()
    sent_messages = fields.Int()
    received_messages = fields.Int()
    system_messages = fields.Int()
    business_messages = fields.Int()
    notification_messages = fields.Int()