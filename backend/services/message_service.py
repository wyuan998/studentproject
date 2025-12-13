# ========================================
# 学生信息管理系统 - 消息服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_, func

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError
from ..models import Message, MessageTemplate, User, db
from ..utils.logger import get_structured_logger


class MessageService(BaseService):
    """消息服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = Message

    # ========================================
    # 消息管理
    # ========================================

    def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送消息

        Args:
            message_data: 消息数据

        Returns:
            Dict[str, Any]: 发送的消息信息

        Raises:
            ServiceError: 发送失败
        """
        try:
            # 验证必填字段
            required_fields = ['sender_id', 'recipient_id', 'title', 'content']
            for field in required_fields:
                if field not in message_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证发送者和接收者存在
            sender = db.session.query(User).filter_by(id=message_data['sender_id']).first()
            if not sender:
                raise ValidationError("发送者不存在", 'sender_id')

            recipient = db.session.query(User).filter_by(id=message_data['recipient_id']).first()
            if not recipient:
                raise ValidationError("接收者不存在", 'recipient_id')

            # 检查权限（只能发送给自己或管理员权限）
            current_user_id = self._get_current_user_id()
            if message_data['sender_id'] != current_user_id:
                self._check_permission('message_management')

            # 创建消息
            message = self.model_class()
            message.sender_id = message_data['sender_id']
            message.recipient_id = message_data['recipient_id']
            message.title = message_data['title']
            message.content = message_data['content']
            message.message_type = message_data.get('message_type', 'personal')
            message.priority = message_data.get('priority', 'normal')
            message.is_read = False

            if 'attachment_path' in message_data:
                message.attachment_path = message_data['attachment_path']
                message.attachment_name = message_data.get('attachment_name', '')

            message.created_at = datetime.utcnow()

            db.session.add(message)
            db.session.commit()

            self._log_business_action('message_sent', {
                'message_id': message.id,
                'sender_id': sender.id,
                'recipient_id': recipient.id,
                'message_type': message.message_type,
                'priority': message.priority
            })

            return message.to_dict()

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"发送消息失败: {str(e)}", message_data=message_data)
            raise ServiceError("消息发送服务异常", 'MESSAGE_SEND_ERROR')

    def mark_as_read(self, message_id: int) -> bool:
        """
        标记消息为已读

        Args:
            message_id: 消息ID

        Returns:
            bool: 是否标记成功

        Raises:
            ServiceError: 标记失败
        """
        try:
            message = self.get_by_id(message_id)
            if not message:
                raise NotFoundError("消息")

            # 检查权限（只能标记自己收到的消息）
            current_user_id = self._get_current_user_id()
            if message.recipient_id != current_user_id:
                self._check_permission('message_management')

            if message.is_read:
                return True  # 已是已读状态

            message.is_read = True
            message.read_at = datetime.utcnow()
            db.session.commit()

            self._log_business_action('message_read', {
                'message_id': message.id,
                'reader_id': current_user_id
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"标记消息已读失败: {str(e)}", message_id=message_id)
            raise ServiceError("消息标记服务异常", 'MESSAGE_READ_ERROR')

    def delete_message(self, message_id: int) -> bool:
        """
        删除消息

        Args:
            message_id: 消息ID

        Returns:
            bool: 是否删除成功

        Raises:
            ServiceError: 删除失败
        """
        try:
            message = self.get_by_id(message_id)
            if not message:
                raise NotFoundError("消息")

            # 检查权限（发送者或接收者可以删除）
            current_user_id = self._get_current_user_id()
            if message.sender_id != current_user_id and message.recipient_id != current_user_id:
                self._check_permission('message_management')

            db.session.delete(message)
            db.session.commit()

            self._log_business_action('message_deleted', {
                'message_id': message_id,
                'deleter_id': current_user_id,
                'was_sender': message.sender_id == current_user_id
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"删除消息失败: {str(e)}", message_id=message_id)
            raise ServiceError("消息删除服务异常", 'MESSAGE_DELETE_ERROR')

    # ========================================
    # 消息查询
    # ========================================

    def get_user_messages(
        self,
        user_id: int = None,
        message_type: str = None,
        is_read: bool = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户消息列表

        Args:
            user_id: 用户ID（默认为当前用户）
            message_type: 消息类型筛选
            is_read: 是否已读筛选
            page: 页码
            per_page: 每页数量

        Returns:
            Dict[str, Any]: 消息列表和分页信息
        """
        try:
            if user_id is None:
                user_id = self._get_current_user_id()

            # 检查权限
            if user_id != self._get_current_user_id():
                self._check_permission('message_management')

            # 构建查询
            query = self.model_class.query.filter(
                or_(
                    self.model_class.sender_id == user_id,
                    self.model_class.recipient_id == user_id
                )
            )

            if message_type:
                query = query.filter(self.model_class.message_type == message_type)
            if is_read is not None:
                query = query.filter(self.model_class.is_read == is_read)

            query = query.order_by(self.model_class.created_at.desc())

            result = self.get_list(
                model_class=self.model_class,
                filters={},  # 使用自定义query
                page=page,
                per_page=per_page
            )

            # 手动执行查询
            per_page = min(per_page, 100)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            # 格式化结果
            messages = []
            for message in pagination.items:
                message_dict = message.to_dict()

                # 添加发送者和接收者信息
                sender = db.session.query(User).filter_by(id=message.sender_id).first()
                recipient = db.session.query(User).filter_by(id=message.recipient_id).first()

                if sender:
                    message_dict['sender'] = {
                        'id': sender.id,
                        'username': sender.username,
                        'name': sender.profile.name if sender.profile else sender.username
                    }

                if recipient:
                    message_dict['recipient'] = {
                        'id': recipient.id,
                        'username': recipient.username,
                        'name': recipient.profile.name if recipient.profile else recipient.username
                    }

                messages.append(message_dict)

            return {
                'messages': messages,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }

        except Exception as e:
            self.logger.error(f"获取用户消息失败: {str(e)}", user_id=user_id)
            raise ServiceError("消息查询服务异常", 'MESSAGE_QUERY_ERROR')

    def get_unread_count(self, user_id: int = None) -> int:
        """
        获取用户未读消息数量

        Args:
            user_id: 用户ID（默认为当前用户）

        Returns:
            int: 未读消息数量
        """
        try:
            if user_id is None:
                user_id = self._get_current_user_id()

            count = self.model_class.query.filter(
                and_(
                    self.model_class.recipient_id == user_id,
                    self.model_class.is_read == False
                )
            ).count()

            return count

        except Exception as e:
            self.logger.error(f"获取未读消息数量失败: {str(e)}", user_id=user_id)
            return 0

    # ========================================
    # 系统消息
    # ========================================

    def send_system_notification(self, title: str, content: str, target_users: List[int] = None, priority: str = 'normal') -> bool:
        """
        发送系统通知

        Args:
            title: 通知标题
            content: 通知内容
            target_users: 目标用户ID列表（None表示所有用户）
            priority: 优先级

        Returns:
            bool: 是否发送成功

        Raises:
            ServiceError: 发送失败
        """
        try:
            self._check_permission('message_management')

            # 获取系统用户ID
            system_user = db.session.query(User).filter_by(username='system').first()
            if not system_user:
                raise ServiceError("系统用户不存在", 'SYSTEM_USER_NOT_FOUND')

            # 确定目标用户
            if target_users is None:
                # 发送给所有活跃用户
                target_users = db.session.query(User.id).filter_by(is_active=True).all()
                target_users = [user.id for user in target_users]

            success_count = 0
            for user_id in target_users:
                try:
                    message = self.model_class()
                    message.sender_id = system_user.id
                    message.recipient_id = user_id
                    message.title = title
                    message.content = content
                    message.message_type = 'system'
                    message.priority = priority
                    message.is_read = False
                    message.created_at = datetime.utcnow()

                    db.session.add(message)
                    success_count += 1
                except Exception as e:
                    self.logger.warning(f"发送系统通知给用户 {user_id} 失败: {str(e)}")

            if success_count > 0:
                db.session.commit()

            self._log_business_action('system_notification_sent', {
                'title': title,
                'target_count': len(target_users),
                'success_count': success_count,
                'priority': priority
            })

            return success_count > 0

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"发送系统通知失败: {str(e)}")
            raise ServiceError("系统通知发送服务异常", 'SYSTEM_NOTIFICATION_ERROR')

    def broadcast_message(self, message_data: Dict[str, Any], target_role: str = None) -> Dict[str, Any]:
        """
        广播消息

        Args:
            message_data: 消息数据
            target_role: 目标角色（None表示所有用户）

        Returns:
            Dict[str, Any]: 广播结果

        Raises:
            ServiceError: 广播失败
        """
        try:
            self._check_permission('message_management')

            # 验证必填字段
            if 'sender_id' not in message_data or 'title' not in message_data or 'content' not in message_data:
                raise ValidationError("缺少必填字段: sender_id, title, content")

            # 获取目标用户
            query = db.session.query(User.id).filter_by(is_active=True)
            if target_role:
                query = query.filter_by(role=target_role)

            target_users = [user.id for user in query.all()]

            # 批量创建消息
            success_count = 0
            failed_count = 0

            for user_id in target_users:
                try:
                    message = self.model_class()
                    message.sender_id = message_data['sender_id']
                    message.recipient_id = user_id
                    message.title = message_data['title']
                    message.content = message_data['content']
                    message.message_type = 'broadcast'
                    message.priority = message_data.get('priority', 'normal')
                    message.is_read = False
                    message.created_at = datetime.utcnow()

                    if 'attachment_path' in message_data:
                        message.attachment_path = message_data['attachment_path']
                        message.attachment_name = message_data.get('attachment_name', '')

                    db.session.add(message)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    self.logger.warning(f"广播消息给用户 {user_id} 失败: {str(e)}")

            if success_count > 0:
                db.session.commit()

            result = {
                'total_targets': len(target_users),
                'success_count': success_count,
                'failed_count': failed_count,
                'success': failed_count == 0
            }

            self._log_business_action('message_broadcasted', {
                'title': message_data['title'],
                'target_role': target_role,
                'total_targets': len(target_users),
                'success_count': success_count
            })

            return result

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"广播消息失败: {str(e)}")
            raise ServiceError("消息广播服务异常", 'MESSAGE_BROADCAST_ERROR')

    # ========================================
    # 消息统计
    # ========================================

    def get_message_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取消息统计信息

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            query = self.model_class.query

            if start_date:
                query = query.filter(self.model_class.created_at >= start_date)
            if end_date:
                query = query.filter(self.model_class.created_at <= end_date)

            # 总数统计
            total_messages = query.count()

            # 按类型统计
            type_stats = db.session.query(
                self.model_class.message_type,
                func.count(self.model_class.id)
            ).group_by(self.model_class.message_type).all()

            # 按优先级统计
            priority_stats = db.session.query(
                self.model_class.priority,
                func.count(self.model_class.id)
            ).group_by(self.model_class.priority).all()

            # 已读/未读统计
            read_stats = db.session.query(
                self.model_class.is_read,
                func.count(self.model_class.id)
            ).group_by(self.model_class.is_read).all()

            return {
                'total_messages': total_messages,
                'type_distribution': {
                    msg_type: count for msg_type, count in type_stats if msg_type
                },
                'priority_distribution': {
                    priority: count for priority, count in priority_stats if priority
                },
                'read_status': {
                    'read': next((count for is_read, count in read_stats if is_read), 0),
                    'unread': next((count for is_read, count in read_stats if not is_read), 0)
                }
            }

        except Exception as e:
            self.logger.error(f"获取消息统计失败: {str(e)}")
            raise ServiceError("消息统计服务异常", 'MESSAGE_STATISTICS_ERROR')

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证消息数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'sender_id' in data:
                sender = db.session.query(User).filter_by(id=data['sender_id']).first()
                if not sender:
                    raise ValidationError("发送者不存在", 'sender_id')

            if 'recipient_id' in data:
                recipient = db.session.query(User).filter_by(id=data['recipient_id']).first()
                if not recipient:
                    raise ValidationError("接收者不存在", 'recipient_id')