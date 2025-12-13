# ========================================
# 学生信息管理系统 - 基础服务类
# ========================================

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from flask import current_app, g
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError

from ..models import db
from ..utils.logger import get_structured_logger
from ..utils.cache import get_cache_manager
from ..utils.responses import APIResponse
from ..utils.validators import BaseValidator


class ServiceError(Exception):
    """服务异常基类"""

    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ServiceError):
    """验证错误"""

    def __init__(self, message: str, field: str = None):
        super().__init__(message, 'VALIDATION_ERROR')
        if field:
            self.details['field'] = field


class NotFoundError(ServiceError):
    """资源未找到错误"""

    def __init__(self, resource_type: str = "资源"):
        super().__init__(f"{resource_type}不存在", 'NOT_FOUND')
        self.details['resource_type'] = resource_type


class PermissionError(ServiceError):
    """权限错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 'PERMISSION_DENIED')


class BusinessRuleError(ServiceError):
    """业务规则错误"""

    def __init__(self, message: str, rule: str = None):
        super().__init__(message, 'BUSINESS_RULE_VIOLATION')
        if rule:
            self.details['rule'] = rule


class BaseService:
    """基础服务类"""

    def __init__(self):
        """初始化基础服务"""
        self.logger = get_structured_logger(self.__class__.__name__)
        self.cache = get_cache_manager()
        self.model_class = None  # 子类需要设置对应的模型类
        self.resource_name = self.__class__.__name__.replace('Service', '').lower()

    # ========================================
    # 数据库操作基础方法
    # ========================================

    def _get_session(self) -> Session:
        """获取数据库会话"""
        return db.session

    def _commit_transaction(self):
        """提交事务"""
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"事务提交失败: {str(e)}")
            raise ServiceError(f"数据库操作失败: {str(e)}")

    def _rollback_transaction(self):
        """回滚事务"""
        db.session.rollback()

    # ========================================
    # 基础CRUD操作
    # ========================================

    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[Any]:
        """
        根据ID获取记录

        Args:
            id: 记录ID
            include_deleted: 是否包含已删除的记录

        Returns:
            Optional[Model]: 模型实例或None
        """
        try:
            cache_key = f"{self.resource_name}:{id}"
            cached_item = self.cache.get(cache_key)

            if cached_item:
                return cached_item

            if not self.model_class:
                raise ServiceError("模型类未设置")

            query = self.model_class.query
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            item = query.get(id)

            if item:
                self.cache.set(cache_key, item, timeout=300)  # 5分钟缓存

            return item

        except SQLAlchemyError as e:
            self.logger.error(f"获取{self.resource_name}失败: {str(e)}")
            raise ServiceError(f"查询失败: {str(e)}")

    def get_by_field(self, field: str, value: Any, include_deleted: bool = False) -> Optional[Any]:
        """
        根据字段值获取记录

        Args:
            field: 字段名
            value: 字段值
            include_deleted: 是否包含已删除的记录

        Returns:
            Optional[Model]: 模型实例或None
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            if not hasattr(self.model_class, field):
                raise ValidationError(f"字段 {field} 不存在")

            query = self.model_class.query.filter(getattr(self.model_class, field) == value)

            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            return query.first()

        except SQLAlchemyError as e:
            self.logger.error(f"根据字段获取{self.resource_name}失败: {str(e)}")
            raise ServiceError(f"查询失败: {str(e)}")

    def get_list(
        self,
        filters: Dict = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = None,
        sort_order: str = 'desc',
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        获取记录列表

        Args:
            filters: 过滤条件
            page: 页码
            per_page: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向 (asc/desc)
            include_deleted: 是否包含已删除的记录

        Returns:
            Dict[str, Any]: 包含数据和分页信息的字典
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            query = self.model_class.query

            # 应用过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model_class, field).in_(value))
                        elif isinstance(value, dict):
                            # 支持复杂查询条件
                            if 'operator' in value:
                                column = getattr(self.model_class, field)
                                operator = value['operator']
                                filter_value = value.get('value')

                                if operator == 'like':
                                    query = query.filter(column.like(f'%{filter_value}%'))
                                elif operator == '>':
                                    query = query.filter(column > filter_value)
                                elif operator == '<':
                                    query = query.filter(column < filter_value)
                                elif operator == '>=':
                                    query = query.filter(column >= filter_value)
                                elif operator == '<=':
                                    query = query.filter(column <= filter_value)
                                elif operator == '!=':
                                    query = query.filter(column != filter_value)
                        else:
                            query = query.filter(getattr(self.model_class, field) == value)

            # 排除已删除记录
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            # 应用排序
            if sort_by and hasattr(self.model_class, sort_by):
                order_column = getattr(self.model_class, sort_by)
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))

            # 分页
            per_page = min(per_page, 100)  # 限制最大每页数量
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return {
                'items': pagination.items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next,
                    'prev_num': pagination.prev_num,
                    'next_num': pagination.next_num
                }
            }

        except SQLAlchemyError as e:
            self.logger.error(f"获取{self.resource_name}列表失败: {str(e)}")
            raise ServiceError(f"查询失败: {str(e)}")

    def create(self, data: Dict[str, Any], validate: bool = True) -> Any:
        """
        创建新记录

        Args:
            data: 创建数据
            validate: 是否进行验证

        Returns:
            Model: 创建的模型实例
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            # 数据验证
            if validate:
                self._validate_data(data, operation='create')

            # 创建实例
            instance = self.model_class()
            for field, value in data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)

            # 设置创建时间
            if hasattr(instance, 'created_at'):
                instance.created_at = datetime.utcnow()

            # 保存到数据库
            db.session.add(instance)
            self._commit_transaction()

            # 清除相关缓存
            self._clear_cache_pattern(f"{self.resource_name}:*")

            self.logger.info(f"创建{self.resource_name}成功",
                           instance_id=instance.id,
                           data=data)

            return instance

        except SQLAlchemyError as e:
            self._rollback_transaction()
            self.logger.error(f"创建{self.resource_name}失败: {str(e)}", data=data)
            raise ServiceError(f"创建失败: {str(e)}")

    def update(self, id: int, data: Dict[str, Any], validate: bool = True) -> Any:
        """
        更新记录

        Args:
            id: 记录ID
            data: 更新数据
            validate: 是否进行验证

        Returns:
            Model: 更新后的模型实例
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            # 获取记录
            instance = self.get_by_id(id)
            if not instance:
                raise NotFoundError(self.resource_name)

            # 数据验证
            if validate:
                self._validate_data(data, operation='update', instance=instance)

            # 更新字段
            for field, value in data.items():
                if hasattr(instance, field) and field != 'id':
                    setattr(instance, field, value)

            # 设置更新时间
            if hasattr(instance, 'updated_at'):
                instance.updated_at = datetime.utcnow()

            # 保存到数据库
            self._commit_transaction()

            # 清除缓存
            cache_key = f"{self.resource_name}:{id}"
            self.cache.delete(cache_key)
            self._clear_cache_pattern(f"{self.resource_name}:*")

            self.logger.info(f"更新{self.resource_name}成功",
                           instance_id=id,
                           data=data)

            return instance

        except SQLAlchemyError as e:
            self._rollback_transaction()
            self.logger.error(f"更新{self.resource_name}失败: {str(e)}",
                           instance_id=id,
                           data=data)
            raise ServiceError(f"更新失败: {str(e)}")

    def delete(self, id: int, soft_delete: bool = True) -> bool:
        """
        删除记录

        Args:
            id: 记录ID
            soft_delete: 是否软删除

        Returns:
            bool: 是否删除成功
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            instance = self.get_by_id(id)
            if not instance:
                raise NotFoundError(self.resource_name)

            if soft_delete and hasattr(instance, 'deleted_at'):
                # 软删除
                instance.deleted_at = datetime.utcnow()
                self.logger.info(f"软删除{self.resource_name}成功", instance_id=id)
            else:
                # 硬删除
                db.session.delete(instance)
                self.logger.info(f"硬删除{self.resource_name}成功", instance_id=id)

            self._commit_transaction()

            # 清除缓存
            cache_key = f"{self.resource_name}:{id}"
            self.cache.delete(cache_key)
            self._clear_cache_pattern(f"{self.resource_name}:*")

            return True

        except SQLAlchemyError as e:
            self._rollback_transaction()
            self.logger.error(f"删除{self.resource_name}失败: {str(e)}", instance_id=id)
            raise ServiceError(f"删除失败: {str(e)}")

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[Any]:
        """
        批量创建记录

        Args:
            data_list: 数据列表

        Returns:
            List[Model]: 创建的模型实例列表
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            instances = []
            for data in data_list:
                # 数据验证
                self._validate_data(data, operation='create')

                instance = self.model_class()
                for field, value in data.items():
                    if hasattr(instance, field):
                        setattr(instance, field, value)

                if hasattr(instance, 'created_at'):
                    instance.created_at = datetime.utcnow()

                instances.append(instance)

            # 批量保存
            db.session.add_all(instances)
            self._commit_transaction()

            # 清除缓存
            self._clear_cache_pattern(f"{self.resource_name}:*")

            self.logger.info(f"批量创建{self.resource_name}成功", count=len(instances))

            return instances

        except SQLAlchemyError as e:
            self._rollback_transaction()
            self.logger.error(f"批量创建{self.resource_name}失败: {str(e)}", count=len(data_list))
            raise ServiceError(f"批量创建失败: {str(e)}")

    def bulk_update(self, updates: List[Dict[str, Any]]) -> bool:
        """
        批量更新记录

        Args:
            updates: 更新数据列表 [{'id': 1, 'field': 'value'}, ...]

        Returns:
            bool: 是否更新成功
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            updated_count = 0
            for update_data in updates:
                id = update_data.pop('id', None)
                if id is None:
                    continue

                instance = self.get_by_id(id)
                if instance:
                    for field, value in update_data.items():
                        if hasattr(instance, field):
                            setattr(instance, field, value)

                    if hasattr(instance, 'updated_at'):
                        instance.updated_at = datetime.utcnow()

                    updated_count += 1

            if updated_count > 0:
                self._commit_transaction()
                # 清除缓存
                self._clear_cache_pattern(f"{self.resource_name}:*")
                self.logger.info(f"批量更新{self.resource_name}成功", count=updated_count)

            return updated_count > 0

        except SQLAlchemyError as e:
            self._rollback_transaction()
            self.logger.error(f"批量更新{self.resource_name}失败: {str(e)}")
            raise ServiceError(f"批量更新失败: {str(e)}")

    # ========================================
    # 业务逻辑辅助方法
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证数据（子类可重写）

        Args:
            data: 要验证的数据
            operation: 操作类型 (create/update)
            instance: 更新时的实例
        """
        pass

    def _check_permission(self, permission: str, resource_id: int = None):
        """
        检查权限

        Args:
            permission: 权限名称
            resource_id: 资源ID
        """
        if not hasattr(g, 'current_user') or not g.current_user:
            raise PermissionError("用户未登录")

        if not g.current_user.has_permission(permission):
            raise PermissionError(f"需要 {permission} 权限")

    def _require_owner_or_permission(self, instance: Any, permission: str, user_field: str = 'user_id'):
        """
        检查是否为资源所有者或具有特定权限

        Args:
            instance: 资源实例
            permission: 权限名称
            user_field: 用户字段名
        """
        if not hasattr(g, 'current_user') or not g.current_user:
            raise PermissionError("用户未登录")

        # 检查是否为资源所有者
        if hasattr(instance, user_field):
            owner_id = getattr(instance, user_field)
            if owner_id == g.current_user.id:
                return

        # 检查权限
        if not g.current_user.has_permission(permission):
            raise PermissionError(f"需要为资源所有者或拥有 {permission} 权限")

    def _get_current_user_id(self) -> int:
        """获取当前用户ID"""
        if hasattr(g, 'current_user') and g.current_user:
            return g.current_user.id
        raise PermissionError("用户未登录")

    def _clear_cache_pattern(self, pattern: str):
        """清除匹配模式的缓存"""
        self.cache.delete_pattern(pattern)

    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        return f"{self.resource_name}:" + ":".join(str(arg) for arg in args)

    def _log_business_action(self, action: str, details: Dict = None):
        """记录业务操作日志"""
        log_data = {
            'action': f"{self.resource_name}_{action}",
            'user_id': self._get_current_user_id(),
            'timestamp': datetime.utcnow().isoformat()
        }

        if details:
            log_data.update(details)

        self.logger.info(f"{self.resource_name}_{action}", **log_data)

    # ========================================
    # 统计和分析方法
    # ========================================

    def count(self, filters: Dict = None, include_deleted: bool = False) -> int:
        """
        统计记录数量

        Args:
            filters: 过滤条件
            include_deleted: 是否包含已删除的记录

        Returns:
            int: 记录数量
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            query = db.session.query(func.count(self.model_class.id))

            # 应用过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.filter(getattr(self.model_class, field) == value)

            # 排除已删除记录
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            return query.scalar() or 0

        except SQLAlchemyError as e:
            self.logger.error(f"统计{self.resource_name}数量失败: {str(e)}")
            raise ServiceError(f"统计失败: {str(e)}")

    def exists(self, id: int) -> bool:
        """
        检查记录是否存在

        Args:
            id: 记录ID

        Returns:
            bool: 是否存在
        """
        try:
            if not self.model_class:
                raise ServiceError("模型类未设置")

            return self.model_class.query.filter(
                and_(
                    self.model_class.id == id,
                    self.model_class.deleted_at.is_(None)
                )
            ).first() is not None

        except SQLAlchemyError as e:
            self.logger.error(f"检查{self.resource_name}存在性失败: {str(e)}")
            return False

    # ========================================
    # 事务管理
    # ========================================

    def transaction(self):
        """
        事务上下文管理器

        Usage:
            with service.transaction():
                # 执行多个数据库操作
                pass
        """
        return TransactionContext(self)


class TransactionContext:
    """事务上下文管理器"""

    def __init__(self, service: BaseService):
        self.service = service

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.service._rollback_transaction()
            raise
        else:
            self.service._commit_transaction()