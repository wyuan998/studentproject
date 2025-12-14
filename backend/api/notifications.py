# ========================================
# 学生信息管理系统 - 消息通知API
# ========================================

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import json

from models import User, Message, MessageTemplate, db
from schemas import MessageSchema, MessageCreateSchema, MessageUpdateSchema
from utils.responses import success_response, error_response, validation_error_response
from utils.decorators import require_permission
from utils.audit import log_action

api = Namespace('notifications', description='消息通知管理')

# 消息模型定义
message_model = api.model('Message', {
    'title': fields.String(required=True, description='消息标题'),
    'content': fields.String(required=True, description='消息内容'),
    'type': fields.String(required=True, enum=['info', 'warning', 'error', 'success'], description='消息类型'),
    'priority': fields.String(enum=['low', 'medium', 'high', 'urgent'], description='优先级'),
    'target_type': fields.String(required=True, enum=['all', 'role', 'users', 'students', 'teachers'], description='目标类型'),
    'target_ids': fields.List(fields.Integer(), description='目标ID列表'),
    'scheduled_at': fields.DateTime(description='计划发送时间'),
    'expires_at': fields.DateTime(description='过期时间')
})

notification_model = api.model('Notification', {
    'read': fields.Boolean(description='是否已读'),
    'archived': fields.Boolean(description='是否已归档')
})

@api.route('/messages')
class MessageListResource(Resource):
    @api.doc('list_messages')
    @api.param('page', '页码', type=int, default=1)
    @api.param('per_page', '每页数量', type=int, default=20)
    @api.param('type', '消息类型')
    @api.param('status', '状态: read/unread/archived')
    @api.param('priority', '优先级')
    @jwt_required()
    def get(self):
        """获取当前用户的消息列表"""
        try:
            current_user_id = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            message_type = request.args.get('type')
            status = request.args.get('status')
            priority = request.args.get('priority')

            # 构建查询
            query = Message.query.filter_by(recipient_id=current_user_id)

            # 筛选条件
            if message_type:
                query = query.filter(Message.type == message_type)

            if status == 'read':
                query = query.filter(Message.is_read == True)
            elif status == 'unread':
                query = query.filter(Message.is_read == False)
            elif status == 'archived':
                query = query.filter(Message.is_archived == True)

            if priority:
                query = query.filter(Message.priority == priority)

            # 排序和分页
            query = query.order_by(desc(Message.created_at), desc(Message.priority))
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            # 序列化数据
            message_schema = MessageSchema()
            messages = message_schema.dump(pagination.items, many=True)

            return success_response({
                'messages': messages,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            })

        except Exception as e:
            current_app.logger.error(f"获取消息列表失败: {str(e)}")
            return error_response("获取消息列表失败")

    @api.doc('create_message')
    @api.expect(message_model)
    @jwt_required()
    @require_permission('message:create')
    def post(self):
        """创建消息"""
        try:
            data = request.get_json()
            current_user_id = get_jwt_identity()

            # 设置发送者
            data['sender_id'] = current_user_id

            # 验证数据
            schema = MessageCreateSchema()
            validated_data = schema.load(data)

            # 处理目标用户
            target_type = validated_data['target_type']
            target_ids = validated_data.get('target_ids', [])

            recipient_ids = []

            if target_type == 'all':
                # 发送给所有用户
                users = User.query.filter_by(is_active=True).all()
                recipient_ids = [user.id for user in users]

            elif target_type == 'role':
                # 发送给特定角色的用户
                if not target_ids:
                    return error_response("角色目标需要指定角色列表", 400)

                users = User.query.filter(
                    User.role.in_(target_ids),
                    User.is_active == True
                ).all()
                recipient_ids = [user.id for user in users]

            elif target_type == 'users':
                # 发送给特定用户
                recipient_ids = target_ids

            elif target_type == 'students':
                # 发送给所有学生
                students = User.query.filter_by(role='student', is_active=True).all()
                recipient_ids = [student.id for student in students]

            elif target_type == 'teachers':
                # 发送给所有教师
                teachers = User.query.filter_by(role='teacher', is_active=True).all()
                recipient_ids = [teacher.id for teacher in teachers]

            # 创建消息
            messages = []
            for recipient_id in recipient_ids:
                message = Message(
                    sender_id=current_user_id,
                    recipient_id=recipient_id,
                    title=validated_data['title'],
                    content=validated_data['content'],
                    type=validated_data['type'],
                    priority=validated_data.get('priority', 'medium'),
                    scheduled_at=validated_data.get('scheduled_at'),
                    expires_at=validated_data.get('expires_at')
                )
                messages.append(message)

            # 批量保存
            db.session.add_all(messages)
            db.session.commit()

            # 记录审计日志
            log_action(
                user_id=current_user_id,
                action='create_message',
                resource_type='message',
                description=f"创建消息，发送给 {len(recipient_ids)} 个用户"
            )

            return success_response({
                'message_id': messages[0].id if messages else None,
                'recipient_count': len(recipient_ids)
            }, f"消息创建成功，将发送给 {len(recipient_ids)} 个用户")

        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建消息失败: {str(e)}")
            return error_response("创建消息失败")

@api.route('/messages/<int:message_id>')
class MessageResource(Resource):
    @api.doc('get_message')
    @jwt_required()
    def get(self, message_id):
        """获取消息详情"""
        try:
            current_user_id = get_jwt_identity()
            message = Message.query.filter_by(
                id=message_id,
                recipient_id=current_user_id
            ).first()

            if not message:
                return error_response("消息不存在", 404)

            # 标记为已读
            if not message.is_read:
                message.is_read = True
                message.read_at = datetime.utcnow()
                db.session.commit()

            # 序列化数据
            schema = MessageSchema()
            message_data = schema.dump(message)

            return success_response(message_data)

        except Exception as e:
            current_app.logger.error(f"获取消息详情失败: {str(e)}")
            return error_response("获取消息详情失败")

    @api.doc('update_message')
    @api.expect(notification_model)
    @jwt_required()
    def put(self, message_id):
        """更新消息状态"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            message = Message.query.filter_by(
                id=message_id,
                recipient_id=current_user_id
            ).first()

            if not message:
                return error_response("消息不存在", 404)

            # 更新状态
            if 'read' in data:
                message.is_read = data['read']
                if data['read']:
                    message.read_at = datetime.utcnow()

            if 'archived' in data:
                message.is_archived = data['archived']
                if data['archived']:
                    message.archived_at = datetime.utcnow()

            db.session.commit()

            return success_response(None, "消息状态更新成功")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新消息状态失败: {str(e)}")
            return error_response("更新消息状态失败")

    @api.doc('delete_message')
    @jwt_required()
    def delete(self, message_id):
        """删除消息"""
        try:
            current_user_id = get_jwt_identity()
            message = Message.query.filter_by(
                id=message_id,
                recipient_id=current_user_id
            ).first()

            if not message:
                return error_response("消息不存在", 404)

            # 软删除
            message.is_deleted = True
            message.deleted_at = datetime.utcnow()
            db.session.commit()

            return success_response(None, "消息删除成功")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除消息失败: {str(e)}")
            return error_response("删除消息失败")

@api.route('/notifications/unread-count')
class UnreadCountResource(Resource):
    @api.doc('get_unread_count')
    @jwt_required()
    def get(self):
        """获取未读消息数量"""
        try:
            current_user_id = get_jwt_identity()
            unread_count = Message.query.filter_by(
                recipient_id=current_user_id,
                is_read=False,
                is_deleted=False
            ).count()

            return success_response({
                'unread_count': unread_count
            })

        except Exception as e:
            current_app.logger.error(f"获取未读消息数量失败: {str(e)}")
            return error_response("获取未读消息数量失败")

@api.route('/notifications/mark-all-read')
class MarkAllReadResource(Resource):
    @api.doc('mark_all_read')
    @jwt_required()
    def post(self):
        """标记所有消息为已读"""
        try:
            current_user_id = get_jwt_identity()

            # 更新所有未读消息
            Message.query.filter_by(
                recipient_id=current_user_id,
                is_read=False,
                is_deleted=False
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })

            db.session.commit()

            return success_response(None, "所有消息已标记为已读")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"标记消息已读失败: {str(e)}")
            return error_response("标记消息已读失败")

@api.route('/notifications/batch-action')
class BatchActionResource(Resource):
    @api.doc('batch_action')
    @api.expect({
        'message_ids': fields.List(fields.Integer(), required=True, description='消息ID列表'),
        'action': fields.String(required=True, enum=['read', 'unread', 'archive', 'delete'], description='操作类型')
    })
    @jwt_required()
    def post(self):
        """批量操作消息"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            message_ids = data.get('message_ids', [])
            action = data.get('action')

            if not message_ids:
                return error_response("消息ID列表不能为空", 400)

            # 查询用户的消息
            messages = Message.query.filter(
                Message.id.in_(message_ids),
                Message.recipient_id == current_user_id,
                Message.is_deleted == False
            ).all()

            # 执行批量操作
            if action == 'read':
                for message in messages:
                    message.is_read = True
                    message.read_at = datetime.utcnow()

            elif action == 'unread':
                for message in messages:
                    message.is_read = False
                    message.read_at = None

            elif action == 'archive':
                for message in messages:
                    message.is_archived = True
                    message.archived_at = datetime.utcnow()

            elif action == 'delete':
                for message in messages:
                    message.is_deleted = True
                    message.deleted_at = datetime.utcnow()

            db.session.commit()

            return success_response({
                'processed_count': len(messages)
            }, f"成功处理 {len(messages)} 条消息")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"批量操作消息失败: {str(e)}")
            return error_response("批量操作消息失败")

@api.route('/templates')
class MessageTemplateResource(Resource):
    @api.doc('list_message_templates')
    @jwt_required()
    @require_permission('message:read')
    def get(self):
        """获取消息模板列表"""
        try:
            templates = MessageTemplate.query.filter_by(is_active=True).all()

            template_list = []
            for template in templates:
                template_list.append({
                    'id': template.id,
                    'name': template.name,
                    'title_template': template.title_template,
                    'content_template': template.content_template,
                    'type': template.type,
                    'description': template.description,
                    'variables': template.variables or []
                })

            return success_response(template_list)

        except Exception as e:
            current_app.logger.error(f"获取消息模板失败: {str(e)}")
            return error_response("获取消息模板失败")

@api.route('/templates/<int:template_id>/preview')
class TemplatePreviewResource(Resource):
    @api.doc('preview_template')
    @api.expect({
        'variables': fields.Raw(description='模板变量值')
    })
    @jwt_required()
    @require_permission('message:read')
    def post(self, template_id):
        """预览消息模板"""
        try:
            data = request.get_json()
            variables = data.get('variables', {})

            template = MessageTemplate.query.get(template_id)
            if not template:
                return error_response("模板不存在", 404)

            # 渲染模板
            def render_template(template_str, vars_dict):
                try:
                    for key, value in vars_dict.items():
                        template_str = template_str.replace(f'{{{key}}}', str(value))
                    return template_str
                except:
                    return template_str

            title = render_template(template.title_template, variables)
            content = render_template(template.content_template, variables)

            return success_response({
                'title': title,
                'content': content,
                'type': template.type
            })

        except Exception as e:
            current_app.logger.error(f"预览模板失败: {str(e)}")
            return error_response("预览模板失败")