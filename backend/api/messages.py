# ========================================
# 学生信息管理系统 - 消息管理API
# ========================================

from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import (
    Message, MessageTemplate, MessageType, MessageStatus, MessagePriority,
    User, AuditLog, AuditAction
)
from schemas import (
    MessageSchema, MessageCreateSchema, MessageUpdateSchema,
    MessageSearchSchema, MessageTemplateSchema,
    MessageTemplateCreateSchema, MessageSendSchema
)
from extensions import db
from utils.responses import (
    success_response, error_response, validation_error_response,
    not_found_response, forbidden_response
)
from utils.decorators import require_permission, rate_limit
from utils.pagination import paginate_query
from utils.email import send_email_notification

# 创建命名空间
messages_ns = Namespace('messages', description='消息管理相关操作')

# 定义数据模型
message_create_model = messages_ns.model('MessageCreate', {
    'receiver_id': fields.String(required=True, description='接收者ID'),
    'title': fields.String(required=True, description='标题'),
    'content': fields.String(required=True, description='内容'),
    'type': fields.String(description='消息类型', enum=['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']),
    'priority': fields.String(description='优先级', enum=['low', 'normal', 'high', 'urgent']),
    'delivery_method': fields.String(description='发送方式', enum=['system', 'email', 'sms', 'push', 'both']),
    'scheduled_at': fields.DateTime(description='计划发送时间'),
    'related_entity_type': fields.String(description='关联实体类型'),
    'related_entity_id': fields.String(description='关联实体ID'),
    'related_action': fields.String(description='关联操作'),
    'attachments': fields.List(fields.Raw, description='附件列表'),
    'tags': fields.List(fields.String, description='标签')
})

message_update_model = messages_ns.model('MessageUpdate', {
    'title': fields.String(description='标题'),
    'content': fields.String(description='内容'),
    'type': fields.String(description='消息类型', enum=['system', 'business', 'notification', 'announcement', 'reminder', 'warning', 'error', 'success']),
    'priority': fields.String(description='优先级', enum=['low', 'normal', 'high', 'urgent']),
    'status': fields.String(description='状态', enum=['unread', 'read', 'archived', 'deleted']),
    'attachments': fields.List(fields.Raw, description='附件列表'),
    'tags': fields.List(fields.String, description='标签')
})

message_search_model = messages_ns.model('MessageSearch', {
    'keyword': fields.String(description='搜索关键词'),
    'type': fields.String(description='消息类型筛选'),
    'priority': fields.String(description='优先级筛选'),
    'status': fields.String(description='状态筛选'),
    'sender_id': fields.String(description='发送者ID'),
    'start_date': fields.Date(description='开始日期'),
    'end_date': fields.Date(description='结束日期'),
    'page': fields.Integer(description='页码', default=1),
    'per_page': fields.Integer(description='每页数量', default=20),
    'sort_by': fields.String(description='排序字段', default='sent_at'),
    'sort_order': fields.String(description='排序方式', default='desc')
})

message_send_model = messages_ns.model('MessageSend', {
    'receiver_ids': fields.List(fields.String, required=True, description='接收者ID列表'),
    'title': fields.String(required=True, description='标题'),
    'content': fields.String(required=True, description='内容'),
    'type': fields.String(description='消息类型'),
    'priority': fields.String(description='优先级'),
    'delivery_method': fields.String(description='发送方式'),
    'scheduled_at': fields.DateTime(description='计划发送时间')
})

@messages_ns.route('')
class MessageListResource(Resource):
    @jwt_required()
    @messages_ns.doc('list_messages')
    @messages_ns.expect(message_search_model)
    def get(self):
        """获取消息列表"""
        try:
            schema = MessageSearchSchema()
            data = schema.load(request.args)

            current_user_id = get_jwt_identity()

            # 构建查询 - 只获取当前用户接收的消息
            query = Message.query.filter_by(receiver_id=current_user_id)

            # 排除已删除的消息
            query = query.filter(Message.status != MessageStatus.DELETED)

            # 关键词搜索
            if data.get('keyword'):
                keyword = f"%{data['keyword']}%"
                query = query.filter(
                    or_(
                        Message.title.like(keyword),
                        Message.content.like(keyword)
                    )
                )

            # 类型筛选
            if data.get('type'):
                query = query.filter(Message.type == MessageType(data['type']))

            # 优先级筛选
            if data.get('priority'):
                query = query.filter(Message.priority == MessagePriority(data['priority']))

            # 状态筛选
            if data.get('status'):
                query = query.filter(Message.status == MessageStatus(data['status']))

            # 发送者筛选
            if data.get('sender_id'):
                query = query.filter(Message.sender_id == data['sender_id'])

            # 日期范围筛选
            if data.get('start_date'):
                query = query.filter(Message.sent_at >= data['start_date'])
            if data.get('end_date'):
                end_date = datetime.combine(data['end_date'], datetime.max.time())
                query = query.filter(Message.sent_at <= end_date)

            # 排序
            sort_field = getattr(Message, data['sort_by'], Message.sent_at)
            if data['sort_order'] == 'desc':
                sort_field = sort_field.desc()

            query = query.order_by(sort_field)

            # 分页
            pagination = paginate_query(query, data['page'], data['per_page'])
            messages = pagination.items

            # 序列化
            message_schema = MessageSchema(many=True)
            message_data = message_schema.dump(messages)

            # 获取未读消息数量
            unread_count = Message.query.filter_by(
                receiver_id=current_user_id,
                status=MessageStatus.UNREAD
            ).count()

            response_data = {
                'messages': message_data,
                'total': pagination.total,
                'unread_count': unread_count,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

            return success_response("获取消息列表成功", response_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @messages_ns.expect(message_create_model)
    @messages_ns.doc('create_message')
    @rate_limit("20/minute")
    def post(self):
        """创建消息"""
        try:
            schema = MessageCreateSchema()
            data = schema.load(request.json)

            current_user_id = get_jwt_identity()
            current_user = g.current_user

            # 验证接收者
            receiver = User.query.get(data['receiver_id'])
            if not receiver:
                return error_response("接收者不存在", 400)

            # 检查权限（非管理员只能发送给特定用户）
            if not current_user.has_permission('message_management'):
                # 学生只能给教师和管理员发消息
                # 教师可以给学生和教师发消息
                if current_user.role.value == 'student':
                    if receiver.role.value not in ['teacher', 'admin']:
                        return forbidden_response("学生只能向教师和管理员发送消息")
                elif current_user.role.value == 'teacher':
                    if receiver.role.value not in ['student', 'teacher', 'admin']:
                        return forbidden_response("教师只能向学生、教师和管理员发送消息")

            # 创建消息
            message = Message(
                sender_id=current_user_id,
                receiver_id=data['receiver_id'],
                title=data['title'],
                content=data['content'],
                type=MessageType(data.get('type', 'notification')),
                priority=MessagePriority(data.get('priority', 'normal')),
                delivery_method=data.get('delivery_method', 'system'),
                scheduled_at=data.get('scheduled_at'),
                related_entity_type=data.get('related_entity_type'),
                related_entity_id=data.get('related_entity_id'),
                related_action=data.get('related_action'),
                attachments=data.get('attachments', []),
                tags=data.get('tags', [])
            )

            # 如果设置了计划发送时间，则暂不发送
            if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                message.status = MessageStatus.UNREAD  # 保持未读状态
                message.save()
            else:
                message.sent_at = datetime.utcnow()
                message.save()

                # 如果需要发送邮件
                if message.delivery_method in ['email', 'both']:
                    try:
                        success, msg = message.send_email()
                        if not success:
                            current_app.logger.error(f"发送邮件失败: {msg}")
                    except Exception as e:
                        current_app.logger.error(f"发送邮件异常: {str(e)}")

            # 记录审计日志
            AuditLog.log_create(
                user_id=current_user_id,
                resource_type='message',
                resource_id=message.id,
                resource_name=f"发送消息给 {receiver.username}: {data['title']}"
            )

            # 返回消息信息
            message_schema = MessageSchema()
            message_data = message_schema.dump(message)

            return success_response("消息创建成功", message_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@messages_ns.route('/<string:message_id>')
class MessageResource(Resource):
    @jwt_required()
    @messages_ns.doc('get_message')
    def get(self, message_id):
        """获取消息详情"""
        try:
            current_user_id = get_jwt_identity()

            message = Message.query.get(message_id)
            if not message:
                return not_found_response("消息不存在")

            # 检查权限：只有发送者或接收者可以查看
            if message.sender_id != current_user_id and message.receiver_id != current_user_id:
                return forbidden_response("权限不足")

            # 自动标记为已读（如果是接收者）
            if message.receiver_id == current_user_id and message.is_unread:
                message.mark_as_read()

            # 序列化
            message_schema = MessageSchema()
            message_data = message_schema.dump(message)

            return success_response("获取消息详情成功", message_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @messages_ns.expect(message_update_model)
    @messages_ns.doc('update_message')
    def put(self, message_id):
        """更新消息"""
        try:
            current_user_id = get_jwt_identity()

            message = Message.query.get(message_id)
            if not message:
                return not_found_response("消息不存在")

            # 检查权限：只有发送者可以更新
            if message.sender_id != current_user_id:
                return forbidden_response("只有发送者可以更新消息")

            schema = MessageUpdateSchema()
            data = schema.load(request.json)

            # 更新消息
            if data.get('title'):
                message.title = data['title']
            if data.get('content'):
                message.content = data['content']
            if data.get('type'):
                message.type = MessageType(data['type'])
            if data.get('priority'):
                message.priority = MessagePriority(data['priority'])

            # 接收者可以更新状态
            if message.receiver_id == current_user_id and data.get('status'):
                if data['status'] == 'read':
                    message.mark_as_read()
                elif data['status'] == 'archived':
                    message.archive()
                elif data['status'] == 'deleted':
                    # 检查删除权限
                    if not g.current_user.has_permission('message_management'):
                        return forbidden_response("只有管理员可以删除消息")
                    message.delete()

            if data.get('attachments'):
                message.attachments = data['attachments']
            if data.get('tags'):
                message.tags = data['tags']

            message.save()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='message',
                resource_id=message_id,
                resource_name=message.title,
                details=f"更新消息: {data}"
            )

            # 返回更新后的消息
            message_schema = MessageSchema()
            message_data = message_schema.dump(message)

            return success_response("消息更新成功", message_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @jwt_required()
    @messages_ns.doc('delete_message')
    def delete(self, message_id):
        """删除消息"""
        try:
            current_user_id = get_jwt_identity()

            message = Message.query.get(message_id)
            if not message:
                return not_found_response("消息不存在")

            # 检查权限：发送者、接收者或有message_management权限的用户可以删除
            can_delete = (
                message.sender_id == current_user_id or
                message.receiver_id == current_user_id or
                g.current_user.has_permission('message_management')
            )

            if not can_delete:
                return forbidden_response("权限不足")

            # 记录审计日志
            AuditLog.log_delete(
                user_id=current_user_id,
                resource_type='message',
                resource_id=message_id,
                resource_name=message.title
            )

            # 删除消息
            db.session.delete(message)
            db.session.commit()

            return success_response("消息删除成功")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@messages_ns.route('/<string:message_id>/read')
class MessageReadResource(Resource):
    @jwt_required()
    @messages_ns.doc('mark_message_read')
    def post(self, message_id):
        """标记消息为已读"""
        try:
            current_user_id = get_jwt_identity()

            message = Message.query.get(message_id)
            if not message:
                return not_found_response("消息不存在")

            # 只有接收者可以标记为已读
            if message.receiver_id != current_user_id:
                return forbidden_response("只有接收者可以标记消息为已读")

            if message.is_unread:
                message.mark_as_read()

                # 记录审计日志
                AuditLog.log_update(
                    user_id=current_user_id,
                    resource_type='message',
                    resource_id=message_id,
                    resource_name=message.title,
                    old_values={'status': 'unread'},
                    new_values={'status': 'read'}
                )

            return success_response("消息已标记为已读")

        except Exception as e:
            return error_response(str(e), 500)

@messages_ns.route('/<string:message_id>/unread')
class MessageUnreadResource(Resource):
    @jwt_required()
    @messages_ns.doc('mark_message_unread')
    def post(self, message_id):
        """标记消息为未读"""
        try:
            current_user_id = get_jwt_identity()

            message = Message.query.get(message_id)
            if not message:
                return not_found_response("消息不存在")

            # 只有接收者可以标记为未读
            if message.receiver_id != current_user_id:
                return forbidden_response("只有接收者可以标记消息为未读")

            message.mark_as_unread()

            # 记录审计日志
            AuditLog.log_update(
                user_id=current_user_id,
                resource_type='message',
                resource_id=message_id,
                resource_name=message.title,
                old_values={'status': 'read'},
                new_values={'status': 'unread'}
            )

            return success_response("消息已标记为未读")

        except Exception as e:
            return error_response(str(e), 500)

@messages_ns.route('/bulk-action')
class MessageBulkActionResource(Resource):
    @jwt_required()
    @messages_ns.doc('bulk_message_action')
    def post(self):
        """批量操作消息"""
        try:
            current_user_id = get_jwt_identity()
            data = request.json

            message_ids = data.get('message_ids', [])
            action = data.get('action')

            if not message_ids:
                return error_response("请选择要操作的消息", 400)

            if action not in ['mark_read', 'mark_unread', 'archive', 'delete']:
                return error_response("无效的操作类型", 400)

            messages = Message.query.filter(
                Message.id.in_(message_ids)
            ).all()

            if not messages:
                return error_response("没有找到要操作的消息", 404)

            updated_count = 0

            for message in messages:
                # 检查权限
                if action == 'delete' and not g.current_user.has_permission('message_management'):
                    return forbidden_response("只有管理员可以删除消息")

                if message.receiver_id != current_user_id:
                    return forbidden_response("只能操作自己接收的消息")

                if action == 'mark_read':
                    if message.is_unread:
                        message.mark_as_read()
                        updated_count += 1
                elif action == 'mark_unread':
                    if message.is_read:
                        message.mark_as_unread()
                        updated_count += 1
                elif action == 'archive':
                    message.archive()
                    updated_count += 1
                elif action == 'delete':
                    db.session.delete(message)
                    updated_count += 1

            db.session.commit()

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.UPDATE,
                user_id=current_user_id,
                resource_type='message',
                description=f"批量操作消息: {action}, 数量: {updated_count}"
            )

            return success_response(f"批量操作成功，处理了 {updated_count} 条消息")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@messages_ns.route('/send-bulk')
class MessageSendBulkResource(Resource):
    @jwt_required()
    @messages_ns.expect(message_send_model)
    @messages_ns.doc('send_bulk_messages')
    @require_permission('message_management')
    @rate_limit("10/minute")
    def post(self):
        """批量发送消息"""
        try:
            schema = MessageSendSchema()
            data = schema.load(request.json)

            current_user_id = get_jwt_identity()
            receiver_ids = data['receiver_ids']

            # 验证接收者
            receivers = User.query.filter(User.id.in_(receiver_ids)).all()
            if len(receivers) != len(receiver_ids):
                return error_response("部分接收者不存在", 400)

            created_messages = []

            for receiver in receivers:
                message = Message(
                    sender_id=current_user_id,
                    receiver_id=receiver.id,
                    title=data['title'],
                    content=data['content'],
                    type=MessageType(data.get('type', 'notification')),
                    priority=MessagePriority(data.get('priority', 'normal')),
                    delivery_method=data.get('delivery_method', 'system'),
                    scheduled_at=data.get('scheduled_at'),
                    sent_at=datetime.utcnow()
                )
                message.save()
                created_messages.append(message)

                # 如果需要发送邮件
                if message.delivery_method in ['email', 'both']:
                    try:
                        success, msg = message.send_email()
                        if not success:
                            current_app.logger.error(f"发送邮件失败给 {receiver.email}: {msg}")
                    except Exception as e:
                        current_app.logger.error(f"发送邮件异常: {str(e)}")

            # 记录审计日志
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user_id=current_user_id,
                resource_type='message',
                description=f"批量发送消息: {data['title']}, 数量: {len(created_messages)}"
            )

            response_data = {
                'sent_count': len(created_messages),
                'receivers': [f"{r.profile.full_name if r.profile else r.username} ({r.email})" for r in receivers]
            }

            return success_response(f"成功发送 {len(created_messages)} 条消息", response_data)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

@messages_ns.route('/stats')
class MessageStatsResource(Resource):
    @jwt_required()
    @messages_ns.doc('get_message_stats')
    def get(self):
        """获取消息统计信息"""
        try:
            current_user_id = get_jwt_identity()

            stats = {}

            # 用户消息统计
            stats['total_messages'] = Message.query.filter_by(receiver_id=current_user_id).count()
            stats['unread_messages'] = Message.query.filter_by(
                receiver_id=current_user_id,
                status=MessageStatus.UNREAD
            ).count()
            stats['sent_messages'] = Message.query.filter_by(sender_id=current_user_id).count()

            # 按类型统计
            stats['messages_by_type'] = db.session.query(
                Message.type, db.func.count(Message.id)
            ).filter_by(receiver_id=current_user_id).group_by(Message.type).all()
            stats['messages_by_type'] = {
                msg_type.value: count for msg_type, count in stats['messages_by_type']
            }

            # 按优先级统计
            stats['messages_by_priority'] = db.session.query(
                Message.priority, db.func.count(Message.id)
            ).filter_by(receiver_id=current_user_id).group_by(Message.priority).all()
            stats['messages_by_priority'] = {
                priority.value: count for priority, count in stats['messages_by_priority']
            }

            # 最近消息
            recent_messages = Message.query.filter_by(receiver_id=current_user_id).order_by(
                Message.sent_at.desc()
            ).limit(10).all()

            message_schema = MessageSchema(many=True, only=('id', 'title', 'sender', 'sent_at', 'is_unread'))
            stats['recent_messages'] = message_schema.dump(recent_messages)

            return success_response("获取消息统计成功", stats)

        except Exception as e:
            return error_response(str(e), 500)

@messages_ns.route('/templates')
class MessageTemplateListResource(Resource):
    @jwt_required()
    @messages_ns.doc('list_message_templates')
    def get(self):
        """获取消息模板列表"""
        try:
            # 只返回激活的模板
            templates = MessageTemplate.query.filter_by(is_active=True).order_by(
                MessageTemplate.name
            ).all()

            template_schema = MessageTemplateSchema(many=True)
            template_data = template_schema.dump(templates)

            return success_response("获取消息模板列表成功", template_data)

        except Exception as e:
            return error_response(str(e), 500)

    @jwt_required()
    @messages_ns.doc('create_message_template')
    @require_permission('message_management')
    def post(self):
        """创建消息模板"""
        try:
            data = request.json
            current_user_id = get_jwt_identity()

            schema = MessageTemplateCreateSchema()
            data = schema.load(data)

            template = MessageTemplate(
                name=data['name'],
                title_template=data['title_template'],
                content_template=data['content_template'],
                type=MessageType(data['type']),
                category=data.get('category'),
                variables=data.get('variables'),
                default_variables=data.get('default_variables'),
                is_active=data.get('is_active', True),
                is_system=data.get('is_system', False),
                created_by=current_user_id
            )
            template.save()

            # 记录审计日志
            AuditLog.log_create(
                user_id=current_user_id,
                resource_type='message_template',
                resource_id=template.id,
                resource_name=f"消息模板: {data['name']}"
            )

            template_schema = MessageTemplateSchema()
            template_data = template_schema.dump(template)

            return success_response("消息模板创建成功", template_data, 201)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)