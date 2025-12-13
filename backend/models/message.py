# ========================================
# 学生信息管理系统 - 消息模型
# ========================================

import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Index, Boolean, JSON
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class MessageType(enum.Enum):
    """消息类型枚举"""
    SYSTEM = "system"        # 系统通知
    BUSINESS = "business"    # 业务通知
    NOTIFICATION = "notification"  # 通知消息
    ANNOUNCEMENT = "announcement"  # 公告
    REMINDER = "reminder"    # 提醒
    WARNING = "warning"      # 警告
    ERROR = "error"         # 错误
    SUCCESS = "success"     # 成功

class MessageStatus(enum.Enum):
    """消息状态枚举"""
    UNREAD = "unread"      # 未读
    READ = "read"          # 已读
    ARCHIVED = "archived"  # 已归档
    DELETED = "deleted"    # 已删除

class MessagePriority(enum.Enum):
    """消息优先级枚举"""
    LOW = "low"           # 低优先级
    NORMAL = "normal"     # 普通优先级
    HIGH = "high"         # 高优先级
    URGENT = "urgent"     # 紧急

class Message(BaseModel):
    """消息模型"""

    __tablename__ = 'messages'

    # 发送和接收信息
    sender_id = Column(db.CHAR(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = Column(db.CHAR(36), db.ForeignKey('users.id'), nullable=False)

    # 消息内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(MessageType), nullable=False, default=MessageType.NOTIFICATION)
    priority = Column(Enum(MessagePriority), default=MessagePriority.NORMAL)

    # 状态信息
    status = Column(Enum(MessageStatus), default=MessageStatus.UNREAD)
    read_at = Column(DateTime)  # 阅读时间

    # 发送信息
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_method = Column(String(20), default='system')  # system, email, sms, push

    # 关联信息
    related_entity_type = Column(String(50))  # 关联实体类型
    related_entity_id = Column(db.CHAR(36))   # 关联实体ID
    related_action = Column(String(50))      # 关联操作

    # 附加信息
    attachments = Column(JSON)  # 附件列表
    metadata = Column(JSON)     # 元数据
    tags = Column(JSON)         # 标签

    # 定时发送
    scheduled_at = Column(DateTime)  # 计划发送时间
    is_recurring = Column(Boolean, default=False)  # 是否重复
    recurring_pattern = Column(JSON)  # 重复模式

    # 邮件相关
    email_sent = Column(Boolean, default=False)  # 是否已发送邮件
    email_sent_at = Column(DateTime)  # 邮件发送时间
    email_status = Column(String(50))  # 邮件发送状态

    # 关系
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")

    # 索引
    __table_args__ = (
        Index('idx_receiver_status', 'receiver_id', 'status'),
        Index('idx_sender_date', 'sender_id', 'sent_at'),
        Index('idx_type_priority', 'type', 'priority'),
        Index('idx_related_entity', 'related_entity_type', 'related_entity_id'),
        Index('idx_scheduled_at', 'scheduled_at'),
    )

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        if not self.sent_at:
            self.sent_at = datetime.utcnow()

    @property
    def is_unread(self):
        """是否未读"""
        return self.status == MessageStatus.UNREAD

    @property
    def is_read(self):
        """是否已读"""
        return self.status == MessageStatus.READ

    @property
    def display_type(self):
        """获取消息类型显示名称"""
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
        return type_mapping.get(self.type, "消息")

    @property
    def display_priority(self):
        """获取优先级显示名称"""
        priority_mapping = {
            MessagePriority.LOW: "低",
            MessagePriority.NORMAL: "普通",
            MessagePriority.HIGH: "高",
            MessagePriority.URGENT: "紧急"
        }
        return priority_mapping.get(self.priority, "普通")

    @property
    def display_status(self):
        """获取状态显示名称"""
        status_mapping = {
            MessageStatus.UNREAD: "未读",
            MessageStatus.READ: "已读",
            MessageStatus.ARCHIVED: "已归档",
            MessageStatus.DELETED: "已删除"
        }
        return status_mapping.get(self.status, "未知")

    def mark_as_read(self):
        """标记为已读"""
        if self.status == MessageStatus.UNREAD:
            self.status = MessageStatus.READ
            self.read_at = datetime.utcnow()
            self.save()

    def mark_as_unread(self):
        """标记为未读"""
        self.status = MessageStatus.UNREAD
        self.read_at = None
        self.save()

    def archive(self):
        """归档消息"""
        self.status = MessageStatus.ARCHIVED
        self.save()

    def delete(self):
        """删除消息"""
        self.status = MessageStatus.DELETED
        self.save()

    def send_email(self):
        """发送邮件通知"""
        if self.email_sent:
            return False, "邮件已发送"

        try:
            from flask_mail import Message as MailMessage
            from flask import current_app
            mail = current_app.extensions.get('mail')
            if not mail:
                return False, "邮件服务未配置"

            mail_message = MailMessage(
                subject=self.title,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[self.receiver.email],
                body=self.content,
                html=self._get_html_content()
            )

            mail.send(mail_message)

            self.email_sent = True
            self.email_sent_at = datetime.utcnow()
            self.email_status = 'sent'
            self.save()

            return True, "邮件发送成功"

        except Exception as e:
            self.email_status = f'failed: {str(e)}'
            self.save()
            return False, f"邮件发送失败: {str(e)}"

    def _get_html_content(self):
        """获取HTML格式的邮件内容"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{self.title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 10px 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-radius: 0 0 5px 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{self.title}</h2>
                </div>
                <div class="content">
                    {self.content.replace('\n', '<br>')}
                </div>
                <div class="footer">
                    <p>此邮件由学生信息管理系统自动发送</p>
                    <p>发送时间: {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def schedule_sending(self, schedule_time):
        """计划发送时间"""
        self.scheduled_at = schedule_time
        self.save()

    def cancel_scheduling(self):
        """取消计划发送"""
        self.scheduled_at = None
        self.save()

    def set_recurring(self, pattern):
        """设置重复发送"""
        self.is_recurring = True
        self.recurring_pattern = pattern
        self.save()

    def cancel_recurring(self):
        """取消重复发送"""
        self.is_recurring = False
        self.recurring_pattern = None
        self.save()

    def add_attachment(self, filename, file_path, file_size=None):
        """添加附件"""
        if not self.attachments:
            self.attachments = []

        attachment = {
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'added_at': datetime.utcnow().isoformat()
        }

        self.attachments.append(attachment)
        self.save()

    def remove_attachment(self, filename):
        """移除附件"""
        if self.attachments:
            self.attachments = [att for att in self.attachments if att['filename'] != filename]
            self.save()

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

    def set_related_entity(self, entity_type, entity_id, action=None):
        """设置关联实体"""
        self.related_entity_type = entity_type
        self.related_entity_id = entity_id
        self.related_action = action
        self.save()

    def get_content_preview(self, length=100):
        """获取内容预览"""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."

    def get_age_hours(self):
        """获取消息年龄（小时）"""
        now = datetime.utcnow()
        age = now - self.sent_at
        return age.total_seconds() / 3600

    def is_urgent(self):
        """是否为紧急消息"""
        return self.priority == MessagePriority.URGENT

    def is_system_message(self):
        """是否为系统消息"""
        return self.type == MessageType.SYSTEM

    def can_be_replied(self):
        """是否可以回复"""
        return self.type not in [MessageType.SYSTEM, MessageType.ANNOUNCEMENT]

    @classmethod
    def get_user_messages(cls, user_id, status=None, type=None, priority=None, limit=50):
        """获取用户消息"""
        query = cls.query.filter_by(receiver_id=user_id)

        if status:
            query = query.filter_by(status=status)
        if type:
            query = query.filter_by(type=type)
        if priority:
            query = query.filter_by(priority=priority)

        return query.order_by(cls.sent_at.desc()).limit(limit).all()

    @classmethod
    def get_unread_count(cls, user_id):
        """获取未读消息数量"""
        return cls.query.filter_by(
            receiver_id=user_id,
            status=MessageStatus.UNREAD
        ).count()

    @classmethod
    def mark_all_as_read(cls, user_id):
        """标记所有消息为已读"""
        messages = cls.query.filter_by(
            receiver_id=user_id,
            status=MessageStatus.UNREAD
        ).all()

        for message in messages:
            message.mark_as_read()

        return len(messages)

    @classmethod
    def get_scheduled_messages(cls):
        """获取待发送的定时消息"""
        now = datetime.utcnow()
        return cls.query.filter(
            cls.scheduled_at <= now,
            cls.sent_at > now  # 还未发送的
        ).all()

    @classmethod
    def send_scheduled_messages(cls):
        """发送定时消息"""
        scheduled_messages = cls.get_scheduled_messages()
        sent_count = 0

        for message in scheduled_messages:
            message.sent_at = datetime.utcnow()
            message.scheduled_at = None
            message.save()

            # 如果需要发送邮件
            if message.delivery_method in ['email', 'both']:
                message.send_email()

            sent_count += 1

        return sent_count

    @classmethod
    def cleanup_old_messages(cls, days=90):
        """清理旧消息（已删除超过指定天数的消息）"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_messages = cls.query.filter(
            cls.status == MessageStatus.DELETED,
            cls.updated_at < cutoff_date
        ).all()

        for message in old_messages:
            db.session.delete(message)

        db.session.commit()
        return len(old_messages)

    def to_dict(self, include_sender=True, include_receiver=True):
        """转换为字典"""
        data = super().to_dict()
        data['display_type'] = self.display_type
        data['display_priority'] = self.display_priority
        data['display_status'] = self.display_status
        data['content_preview'] = self.get_content_preview()
        data['age_hours'] = self.get_age_hours()

        if include_sender and self.sender:
            data['sender'] = {
                'id': self.sender.id,
                'username': self.sender.username,
                'name': self.sender.profile.full_name if self.sender.profile else self.sender.username,
                'role': self.sender.role.value
            }

        if include_receiver and self.receiver:
            data['receiver'] = {
                'id': self.receiver.id,
                'username': self.receiver.username,
                'name': self.receiver.profile.full_name if self.receiver.profile else self.receiver.username,
                'email': self.receiver.email
            }

        return data

    def __repr__(self):
        return f"<Message(title='{self.title}', type='{self.type.value}', status='{self.status.value}', receiver='{self.receiver.username if self.receiver else 'Unknown'}')>"


class MessageTemplate(BaseModel):
    """消息模板模型"""

    __tablename__ = 'message_templates'

    # 基本信息
    name = Column(String(100), unique=True, nullable=False)
    title_template = Column(String(200), nullable=False)  # 标题模板
    content_template = Column(Text, nullable=False)  # 内容模板

    # 分类信息
    type = Column(Enum(MessageType), nullable=False)
    category = Column(String(50))  # 分类

    # 模板变量
    variables = Column(JSON)  # 可用变量列表
    default_variables = Column(JSON)  # 默认变量值

    # 使用统计
    usage_count = Column(db.Integer, default=0)
    last_used_at = Column(DateTime)

    # 状态
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 是否为系统模板

    # 创建者
    created_by = Column(db.CHAR(36), db.ForeignKey('users.id'))
    updated_by = Column(db.CHAR(36), db.ForeignKey('users.id'))

    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    def render(self, variables=None):
        """渲染模板"""
        variables = variables or {}
        variables.update(self.default_variables or {})

        title = self.title_template.format(**variables)
        content = self.content_template.format(**variables)

        return title, content

    def preview(self, sample_variables=None):
        """预览模板"""
        sample_variables = sample_variables or {}
        return self.render(sample_variables)

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count = (self.usage_count or 0) + 1
        self.last_used_at = datetime.utcnow()
        self.save()

    def __repr__(self):
        return f"<MessageTemplate(name='{self.name}', type='{self.type.value}', active={self.is_active})>"