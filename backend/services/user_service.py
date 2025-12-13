# ========================================
# 学生信息管理系统 - 用户服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError, BusinessRuleError
from ..models import User, UserProfile, db
from ..utils.auth import AuthManager, PasswordManager
from ..utils.validators import PersonalInfoValidator
from ..utils.email import send_welcome_email
from ..utils.logger import get_structured_logger


class UserService(BaseService):
    """用户服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = User
        self.auth_manager = AuthManager()
        self.password_manager = PasswordManager()

    # ========================================
    # 用户认证相关
    # ========================================

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户认证

        Args:
            username: 用户名或邮箱
            password: 密码

        Returns:
            Dict[str, Any]: 认证结果，包含用户信息和令牌

        Raises:
            ServiceError: 认证失败
        """
        try:
            # 查找用户（支持用户名或邮箱）
            user = self.model_class.query.filter(
                or_(
                    self.model_class.username == username,
                    self.model_class.email == username
                )
            ).first()

            if not user:
                self._log_business_action('login_failed', {
                    'username': username,
                    'reason': 'user_not_found'
                })
                raise ServiceError("用户名或密码错误", 'AUTH_FAILED')

            if not user.is_active():
                self._log_business_action('login_failed', {
                    'user_id': user.id,
                    'reason': 'account_disabled'
                })
                raise ServiceError("账户已被禁用", 'ACCOUNT_DISABLED')

            # 验证密码
            if not self.auth_manager.verify_password(password, user.password_hash):
                self._log_business_action('login_failed', {
                    'user_id': user.id,
                    'reason': 'invalid_password'
                })
                raise ServiceError("用户名或密码错误", 'AUTH_FAILED')

            # 生成令牌
            tokens = self.auth_manager.generate_tokens(
                user.id,
                {
                    'role': user.role.value,
                    'permissions': user.get_permissions()
                }
            )

            # 更新最后登录时间
            user.last_login_at = datetime.utcnow()
            db.session.commit()

            # 记录成功登录
            self._log_business_action('login_success', {
                'user_id': user.id,
                'login_time': user.last_login_at.isoformat()
            })

            return {
                'user': user.to_dict(include_sensitive=False),
                'tokens': tokens
            }

        except Exception as e:
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"用户认证失败: {str(e)}", username=username)
            raise ServiceError("认证服务异常", 'AUTH_SERVICE_ERROR')

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            Dict[str, Any]: 新的令牌信息

        Raises:
            ServiceError: 刷新失败
        """
        try:
            tokens = self.auth_manager.refresh_access_token(refresh_token)
            return {'tokens': tokens}

        except Exception as e:
            self.logger.error(f"刷新令牌失败: {str(e)}")
            raise ServiceError("令牌刷新失败", 'TOKEN_REFRESH_FAILED')

    def logout_user(self, refresh_token: str = None) -> bool:
        """
        用户登出

        Args:
            refresh_token: 刷新令牌（可选）

        Returns:
            bool: 是否登出成功
        """
        try:
            # 记录登出
            self._log_business_action('logout', {
                'user_id': self._get_current_user_id()
            })

            # 如果提供了刷新令牌，将其加入黑名单
            if refresh_token:
                # 这里可以实现令牌黑名单逻辑
                pass

            return True

        except Exception as e:
            self.logger.error(f"用户登出失败: {str(e)}")
            return False

    # ========================================
    # 用户注册
    # ========================================

    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        用户注册

        Args:
            user_data: 用户数据

        Returns:
            Dict[str, Any]: 创建的用户信息

        Raises:
            ServiceError: 注册失败
        """
        try:
            # 验证必填字段
            required_fields = ['username', 'email', 'password', 'role']
            for field in required_fields:
                if field not in user_data:
                    raise ValidationError(f"缺少必填字段: {field}", field)

            # 验证用户名
            username_validation = PersonalInfoValidator.validate_name(
                user_data['username'],
                min_length=3,
                max_length=20
            )
            if not username_validation['valid']:
                raise ValidationError(username_validation['message'], 'username')

            # 验证邮箱
            email_validation = PersonalInfoValidator.validate_email(user_data['email'])
            if not email_validation['valid']:
                raise ValidationError(email_validation['message'], 'email')

            # 验证密码强度
            password_validation = PasswordManager.validate_password_strength(user_data['password'])
            if not password_validation['valid']:
                raise ValidationError("密码强度不足", 'password')

            # 检查用户名是否已存在
            if self.get_by_field('username', user_data['username']):
                raise BusinessRuleError("用户名已存在", 'username_exists')

            # 检查邮箱是否已存在
            if self.get_by_field('email', email_validation['normalized']):
                raise BusinessRuleError("邮箱已被注册", 'email_exists')

            # 创建用户
            user = self.model_class()
            user.username = user_data['username']
            user.email = email_validation['normalized']
            user.password_hash = self.auth_manager.hash_password(user_data['password'])
            user.role = user_data['role']
            user.is_active = True
            user.created_at = datetime.utcnow()

            # 创建用户档案
            if user_data.get('profile'):
                profile_data = user_data['profile']
                profile = UserProfile()
                for field, value in profile_data.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
                profile.created_at = datetime.utcnow()
                user.profile = profile

            db.session.add(user)
            db.session.commit()

            # 发送欢迎邮件
            try:
                send_welcome_email(
                    user.email,
                    {
                        'name': user.profile.name if user.profile else user.username,
                        'username': user.username,
                        'email': user.email
                    }
                )
            except Exception as e:
                self.logger.warning(f"发送欢迎邮件失败: {str(e)}")

            # 记录注册
            self._log_business_action('register', {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            })

            return user.to_dict(include_sensitive=False)

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"用户注册失败: {str(e)}", user_data=user_data)
            raise ServiceError("注册服务异常", 'REGISTER_SERVICE_ERROR')

    # ========================================
    # 用户信息管理
    # ========================================

    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        修改密码

        Args:
            old_password: 旧密码
            new_password: 新密码

        Returns:
            bool: 是否修改成功

        Raises:
            ServiceError: 修改失败
        """
        try:
            user_id = self._get_current_user_id()
            user = self.get_by_id(user_id)

            if not user:
                raise NotFoundError("用户")

            # 验证旧密码
            if not self.auth_manager.verify_password(old_password, user.password_hash):
                raise ServiceError("旧密码错误", 'INVALID_OLD_PASSWORD')

            # 验证新密码强度
            password_validation = PasswordManager.validate_password_strength(new_password)
            if not password_validation['valid']:
                raise ValidationError("新密码强度不足", 'password')

            # 检查新密码是否与旧密码相同
            if self.auth_manager.verify_password(new_password, user.password_hash):
                raise BusinessRuleError("新密码不能与旧密码相同", 'same_password')

            # 更新密码
            user.password_hash = self.auth_manager.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()

            # 清除用户相关缓存
            self._clear_cache_pattern(f"user:{user_id}:*")

            # 记录密码修改
            self._log_business_action('password_changed', {
                'user_id': user_id
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"修改密码失败: {str(e)}")
            raise ServiceError("密码修改服务异常", 'PASSWORD_CHANGE_ERROR')

    def reset_password_request(self, email: str) -> Dict[str, Any]:
        """
        密码重置请求

        Args:
            email: 邮箱地址

        Returns:
            Dict[str, Any]: 重置信息

        Raises:
            ServiceError: 请求失败
        """
        try:
            # 验证邮箱格式
            email_validation = PersonalInfoValidator.validate_email(email)
            if not email_validation['valid']:
                raise ValidationError("邮箱格式不正确", 'email')

            # 查找用户
            user = self.get_by_field('email', email_validation['normalized'])
            if not user:
                # 为了安全，即使用户不存在也返回成功
                return {'message': '如果邮箱存在，重置链接已发送'}

            # 生成重置令牌（有效期24小时）
            reset_token = self.password_manager.generate_password(32)
            reset_expiry = datetime.utcnow() + timedelta(hours=24)

            user.reset_token = reset_token
            user.reset_token_expiry = reset_expiry
            user.updated_at = datetime.utcnow()
            db.session.commit()

            # 发送重置邮件（这里应该实现邮件发送逻辑）
            # send_password_reset_email(user.email, {'reset_token': reset_token})

            self._log_business_action('password_reset_requested', {
                'user_id': user.id,
                'email': user.email
            })

            return {'message': '重置链接已发送到您的邮箱'}

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"密码重置请求失败: {str(e)}")
            raise ServiceError("密码重置服务异常", 'PASSWORD_RESET_ERROR')

    def reset_password(self, token: str, new_password: str) -> bool:
        """
        重置密码

        Args:
            token: 重置令牌
            new_password: 新密码

        Returns:
            bool: 是否重置成功

        Raises:
            ServiceError: 重置失败
        """
        try:
            # 查找有效令牌
            user = self.model_class.query.filter(
                and_(
                    self.model_class.reset_token == token,
                    self.model_class.reset_token_expiry > datetime.utcnow()
                )
            ).first()

            if not user:
                raise ServiceError("重置令牌无效或已过期", 'INVALID_TOKEN')

            # 验证新密码强度
            password_validation = PasswordManager.validate_password_strength(new_password)
            if not password_validation['valid']:
                raise ValidationError("新密码强度不足", 'password')

            # 更新密码
            user.password_hash = self.auth_manager.hash_password(new_password)
            user.reset_token = None
            user.reset_token_expiry = None
            user.updated_at = datetime.utcnow()
            db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"user:{user.id}:*")

            self._log_business_action('password_reset', {
                'user_id': user.id
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"密码重置失败: {str(e)}")
            raise ServiceError("密码重置服务异常", 'PASSWORD_RESET_ERROR')

    def update_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户档案

        Args:
            profile_data: 档案数据

        Returns:
            Dict[str, Any]: 更新后的用户信息

        Raises:
            ServiceError: 更新失败
        """
        try:
            user_id = self._get_current_user_id()
            user = self.get_by_id(user_id)

            if not user:
                raise NotFoundError("用户")

            # 获取或创建用户档案
            if not user.profile:
                user.profile = UserProfile()
                user.profile.created_at = datetime.utcnow()

            # 验证和更新档案信息
            profile = user.profile
            for field, value in profile_data.items():
                if hasattr(profile, field) and field != 'user_id':
                    if field == 'email':
                        # 验证邮箱格式
                        email_validation = PersonalInfoValidator.validate_email(value)
                        if not email_validation['valid']:
                            raise ValidationError(email_validation['message'], 'email')

                        # 检查邮箱是否已被其他用户使用
                        existing_user = self.get_by_field('email', email_validation['normalized'])
                        if existing_user and existing_user.id != user_id:
                            raise BusinessRuleError("邮箱已被其他用户使用", 'email_exists')

                        # 更新用户表中的邮箱
                        user.email = email_validation['normalized']
                    elif field == 'phone':
                        # 验证手机号
                        phone_validation = PersonalInfoValidator.validate_phone_number(value)
                        if not phone_validation['valid']:
                            raise ValidationError(phone_validation['message'], 'phone')
                        setattr(profile, field, phone_validation['formatted'])
                    else:
                        setattr(profile, field, value)

            profile.updated_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()

            db.session.commit()

            # 清除缓存
            self._clear_cache_pattern(f"user:{user_id}:*")

            self._log_business_action('profile_updated', {
                'user_id': user_id
            })

            return user.to_dict(include_sensitive=False)

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"更新用户档案失败: {str(e)}")
            raise ServiceError("档案更新服务异常", 'PROFILE_UPDATE_ERROR')

    # ========================================
    # 用户状态管理
    # ========================================

    def activate_user(self, user_id: int) -> bool:
        """
        激活用户

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否激活成功

        Raises:
            ServiceError: 激活失败
        """
        try:
            self._check_permission('user_management')

            user = self.get_by_id(user_id)
            if not user:
                raise NotFoundError("用户")

            user.is_active = True
            user.updated_at = datetime.utcnow()
            db.session.commit()

            self._log_business_action('user_activated', {
                'target_user_id': user_id
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"激活用户失败: {str(e)}")
            raise ServiceError("用户激活服务异常", 'USER_ACTIVATE_ERROR')

    def deactivate_user(self, user_id: int, reason: str = None) -> bool:
        """
        停用用户

        Args:
            user_id: 用户ID
            reason: 停用原因

        Returns:
            bool: 是否停用成功

        Raises:
            ServiceError: 停用失败
        """
        try:
            self._check_permission('user_management')

            user = self.get_by_id(user_id)
            if not user:
                raise NotFoundError("用户")

            # 不能停用自己
            if user_id == self._get_current_user_id():
                raise BusinessRuleError("不能停用自己的账户", 'cannot_deactivate_self')

            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.session.commit()

            self._log_business_action('user_deactivated', {
                'target_user_id': user_id,
                'reason': reason
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"停用用户失败: {str(e)}")
            raise ServiceError("用户停用服务异常", 'USER_DEACTIVATE_ERROR')

    # ========================================
    # 权限和角色管理
    # ========================================

    def change_user_role(self, user_id: int, new_role: str) -> bool:
        """
        修改用户角色

        Args:
            user_id: 用户ID
            new_role: 新角色

        Returns:
            bool: 是否修改成功

        Raises:
            ServiceError: 修改失败
        """
        try:
            self._check_permission('user_management')

            user = self.get_by_id(user_id)
            if not user:
                raise NotFoundError("用户")

            # 验证角色
            valid_roles = ['admin', 'teacher', 'student']
            if new_role not in valid_roles:
                raise ValidationError(f"无效的角色: {new_role}", 'role')

            # 不能修改自己的角色
            if user_id == self._get_current_user_id():
                raise BusinessRuleError("不能修改自己的角色", 'cannot_change_own_role')

            user.role = new_role
            user.updated_at = datetime.utcnow()
            db.session.commit()

            self._log_business_action('user_role_changed', {
                'target_user_id': user_id,
                'old_role': user.role.value,
                'new_role': new_role
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"修改用户角色失败: {str(e)}")
            raise ServiceError("角色修改服务异常", 'ROLE_CHANGE_ERROR')

    # ========================================
    # 用户统计和分析
    # ========================================

    def get_user_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取用户统计信息

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            from sqlalchemy import func

            # 基础查询
            query = self.model_class.query

            # 应用时间过滤
            if start_date:
                query = query.filter(self.model_class.created_at >= start_date)
            if end_date:
                query = query.filter(self.model_class.created_at <= end_date)

            # 总用户数
            total_users = query.count()

            # 按角色统计
            role_stats = db.session.query(
                self.model_class.role,
                func.count(self.model_class.id)
            ).group_by(self.model_class.role).all()

            # 按状态统计
            active_users = query.filter(self.model_class.is_active == True).count()
            inactive_users = total_users - active_users

            # 按时间统计（本月新注册用户）
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_users_this_month = query.filter(
                self.model_class.created_at >= current_month_start
            ).count()

            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'new_users_this_month': new_users_this_month,
                'role_distribution': {
                    role.value: count for role, count in role_stats
                }
            }

        except Exception as e:
            self.logger.error(f"获取用户统计失败: {str(e)}")
            raise ServiceError("统计服务异常", 'STATISTICS_ERROR')

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证用户数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'username' in data:
                # 验证用户名格式
                username_validation = PersonalInfoValidator.validate_name(
                    data['username'],
                    min_length=3,
                    max_length=20
                )
                if not username_validation['valid']:
                    raise ValidationError(username_validation['message'], 'username')

                # 检查用户名唯一性
                if self.get_by_field('username', data['username']):
                    raise BusinessRuleError("用户名已存在", 'username_exists')

            if 'email' in data:
                # 验证邮箱格式
                email_validation = PersonalInfoValidator.validate_email(data['email'])
                if not email_validation['valid']:
                    raise ValidationError(email_validation['message'], 'email')

                # 检查邮箱唯一性
                if self.get_by_field('email', email_validation['normalized']):
                    raise BusinessRuleError("邮箱已被注册", 'email_exists')

        elif operation == 'update':
            # 更新时的验证
            if 'username' in data:
                username_validation = PersonalInfoValidator.validate_name(
                    data['username'],
                    min_length=3,
                    max_length=20
                )
                if not username_validation['valid']:
                    raise ValidationError(username_validation['message'], 'username')

                # 检查用户名唯一性（排除当前用户）
                existing_user = self.get_by_field('username', data['username'])
                if existing_user and existing_user.id != instance.id:
                    raise BusinessRuleError("用户名已存在", 'username_exists')

            if 'email' in data:
                email_validation = PersonalInfoValidator.validate_email(data['email'])
                if not email_validation['valid']:
                    raise ValidationError(email_validation['message'], 'email')

                # 检查邮箱唯一性（排除当前用户）
                existing_user = self.get_by_field('email', email_validation['normalized'])
                if existing_user and existing_user.id != instance.id:
                    raise BusinessRuleError("邮箱已被使用", 'email_exists')