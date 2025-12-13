# ========================================
# 学生信息管理系统 - 限流工具类
# ========================================

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from flask import request, current_app, g
from functools import wraps

# 全局限流器实例
_rate_limiter = None


class RateLimiter:
    """限流器"""

    def __init__(self, storage_backend='memory'):
        """
        初始化限流器

        Args:
            storage_backend: 存储后端 ('memory', 'redis', 'database')
        """
        self.storage_backend = storage_backend
        self._init_storage()

    def _init_storage(self):
        """初始化存储后端"""
        if self.storage_backend == 'memory':
            self.storage = MemoryStorage()
        elif self.storage_backend == 'redis':
            self.storage = RedisStorage()
        elif self.storage_backend == 'database':
            self.storage = DatabaseStorage()
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")

    def is_allowed(self, key: str, limit: str, identifier: Optional[str] = None) -> bool:
        """
        检查是否允许请求

        Args:
            key: 限流键名
            limit: 限流规则 (如 "10/minute", "100/hour")
            identifier: 标识符（默认使用IP地址）

        Returns:
            bool: 是否允许请求
        """
        # 解析限流规则
        max_requests, period_seconds = self._parse_limit(limit)

        # 生成唯一的限流键
        if identifier is None:
            identifier = self._get_identifier()

        rate_key = f"rate_limit:{key}:{identifier}"

        # 检查并更新计数
        return self.storage.is_allowed(rate_key, max_requests, period_seconds)

    def get_remaining(self, key: str, limit: str, identifier: Optional[str] = None) -> int:
        """
        获取剩余请求次数

        Args:
            key: 限流键名
            limit: 限流规则
            identifier: 标识符

        Returns:
            int: 剩余请求次数
        """
        max_requests, period_seconds = self._parse_limit(limit)

        if identifier is None:
            identifier = self._get_identifier()

        rate_key = f"rate_limit:{key}:{identifier}"

        return self.storage.get_remaining(rate_key, max_requests, period_seconds)

    def reset(self, key: str, identifier: Optional[str] = None) -> bool:
        """
        重置限流计数

        Args:
            key: 限流键名
            identifier: 标识符

        Returns:
            bool: 是否成功重置
        """
        if identifier is None:
            identifier = self._get_identifier()

        rate_key = f"rate_limit:{key}:{identifier}"
        return self.storage.reset(rate_key)

    def _parse_limit(self, limit: str) -> tuple:
        """
        解析限流规则

        Args:
            limit: 限流字符串 (如 "10/minute")

        Returns:
            tuple: (最大请求数, 时间周期秒数)
        """
        try:
            parts = limit.split('/')
            if len(parts) != 2:
                raise ValueError("无效的限流格式")

            max_requests = int(parts[0])
            period_str = parts[1].lower()

            # 时间单位映射
            time_units = {
                'second': 1,
                'seconds': 1,
                's': 1,
                'minute': 60,
                'minutes': 60,
                'm': 60,
                'hour': 3600,
                'hours': 3600,
                'h': 3600,
                'day': 86400,
                'days': 86400,
                'd': 86400,
                'week': 604800,
                'weeks': 604800,
                'w': 604800,
                'month': 2592000,  # 30天
                'months': 2592000,
                'y': 31536000  # 365天
            }

            if period_str not in time_units:
                raise ValueError(f"不支持的时间单位: {period_str}")

            period_seconds = time_units[period_str]
            return max_requests, period_seconds

        except Exception as e:
            current_app.logger.error(f"解析限流规则失败: {limit}, 错误: {str(e)}")
            # 默认值：每分钟10次
            return 10, 60

    def _get_identifier(self) -> str:
        """获取请求标识符"""
        # 优先使用用户ID
        if hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"

        # 其次使用IP地址
        return request.environ.get('REMOTE_ADDR', 'unknown')


class MemoryStorage:
    """内存存储"""

    def __init__(self):
        self.data = defaultdict(lambda: deque())
        self.lock = threading.Lock()

    def is_allowed(self, key: str, max_requests: int, period_seconds: int) -> bool:
        """检查是否允许请求"""
        now = time.time()
        cutoff_time = now - period_seconds

        with self.lock:
            timestamps = self.data[key]

            # 清理过期记录
            while timestamps and timestamps[0] <= cutoff_time:
                timestamps.popleft()

            # 检查是否超过限制
            if len(timestamps) >= max_requests:
                return False

            # 添加当前请求
            timestamps.append(now)
            return True

    def get_remaining(self, key: str, max_requests: int, period_seconds: int) -> int:
        """获取剩余请求次数"""
        now = time.time()
        cutoff_time = now - period_seconds

        with self.lock:
            timestamps = self.data[key]

            # 清理过期记录
            while timestamps and timestamps[0] <= cutoff_time:
                timestamps.popleft()

            return max(0, max_requests - len(timestamps))

    def reset(self, key: str) -> bool:
        """重置计数"""
        with self.lock:
            if key in self.data:
                del self.data[key]
                return True
            return False


class RedisStorage:
    """Redis存储"""

    def __init__(self):
        try:
            from extensions import cache
            self.redis_client = cache
        except ImportError:
            raise ImportError("需要安装redis: pip install redis")

    def is_allowed(self, key: str, max_requests: int, period_seconds: int) -> bool:
        """使用Redis滑动窗口算法"""
        try:
            now = int(time.time())
            pipeline = self.redis_client.redis_client.pipeline()

            # 清理过期的键
            pipeline.zremrangebyscore(key, 0, now - period_seconds)

            # 获取当前计数
            pipeline.zcard(key)

            # 添加当前请求
            pipeline.zadd(key, {str(now): now})

            # 设置过期时间
            pipeline.expire(key, period_seconds)

            results = pipeline.execute()
            current_count = results[1]

            return current_count < max_requests

        except Exception as e:
            current_app.logger.error(f"Redis限流检查失败: {str(e)}")
            # 降级到允许请求
            return True

    def get_remaining(self, key: str, max_requests: int, period_seconds: int) -> int:
        """获取剩余请求次数"""
        try:
            now = int(time.time())
            self.redis_client.redis_client.zremrangebyscore(key, 0, now - period_seconds)
            current_count = self.redis_client.redis_client.zcard(key)
            return max(0, max_requests - current_count)
        except Exception:
            return max_requests

    def reset(self, key: str) -> bool:
        """重置计数"""
        try:
            self.redis_client.redis_client.delete(key)
            return True
        except Exception:
            return False


class DatabaseStorage:
    """数据库存储"""

    def is_allowed(self, key: str, max_requests: int, period_seconds: int) -> bool:
        """使用数据库记录"""
        try:
            from models import db, RateLimitRecord
            from sqlalchemy import func

            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=period_seconds)

            # 查询当前时间窗口内的请求数
            count = db.session.query(func.count(RateLimitRecord.id))\
                           .filter(RateLimitRecord.rate_key == key)\
                           .filter(RateLimitRecord.created_at >= cutoff_time)\
                           .scalar()

            if count >= max_requests:
                return False

            # 记录当前请求
            record = RateLimitRecord(rate_key=key, created_at=now)
            db.session.add(record)

            # 清理过期记录（定期执行，避免数据库膨胀）
            if count % 100 == 0:  # 每100次请求清理一次
                db.session.query(RateLimitRecord)\
                         .filter(RateLimitRecord.created_at < cutoff_time)\
                         .delete()

            db.session.commit()
            return True

        except Exception as e:
            current_app.logger.error(f"数据库限流检查失败: {str(e)}")
            db.session.rollback()
            # 降级到允许请求
            return True

    def get_remaining(self, key: str, max_requests: int, period_seconds: int) -> int:
        """获取剩余请求次数"""
        try:
            from models import db, RateLimitRecord
            from sqlalchemy import func

            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=period_seconds)

            count = db.session.query(func.count(RateLimitRecord.id))\
                           .filter(RateLimitRecord.rate_key == key)\
                           .filter(RateLimitRecord.created_at >= cutoff_time)\
                           .scalar()

            return max(0, max_requests - count)

        except Exception:
            return max_requests

    def reset(self, key: str) -> bool:
        """重置计数"""
        try:
            from models import db, RateLimitRecord

            db.session.query(RateLimitRecord)\
                     .filter(RateLimitRecord.rate_key == key)\
                     .delete()
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            return False


class RateLimitConfig:
    """限流配置"""

    # 默认限流规则
    DEFAULT_RULES = {
        'login': '5/minute',       # 登录：每分钟5次
        'register': '3/hour',      # 注册：每小时3次
        'password_reset': '3/hour', # 密码重置：每小时3次
        'api': '1000/hour',       # API调用：每小时1000次
        'upload': '10/minute',     # 文件上传：每分钟10次
        'email': '10/hour',        # 邮件发送：每小时10次
        'search': '60/minute',     # 搜索：每分钟60次
        'export': '5/hour',        # 数据导出：每小时5次
    }

    # 用户角色限流规则
    ROLE_RULES = {
        'admin': '5000/hour',      # 管理员：每小时5000次
        'teacher': '2000/hour',    # 教师：每小时2000次
        'student': '1000/hour',    # 学生：每小时1000次
        'guest': '100/hour',       # 访客：每小时100次
    }

    @classmethod
    def get_limit(cls, key: str, user_role: Optional[str] = None) -> str:
        """
        获取限流规则

        Args:
            key: 限流键名
            user_role: 用户角色

        Returns:
            str: 限流规则
        """
        # 优先使用角色限流
        if user_role and user_role in cls.ROLE_RULES:
            return cls.ROLE_RULES[user_role]

        # 使用默认规则
        return cls.DEFAULT_RULES.get(key, '1000/hour')


# 全局限流器实例
def get_rate_limiter() -> RateLimiter:
    """获取全局限流器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        storage_backend = current_app.config.get('RATE_LIMIT_STORAGE', 'memory')
        _rate_limiter = RateLimiter(storage_backend)
    return _rate_limiter


# 装饰器
def rate_limit(limit: str, key: Optional[str] = None, per_user: bool = False):
    """
    限流装饰器

    Args:
        limit: 限流规则 (如 "10/minute")
        key: 限流键名
        per_user: 是否按用户限流

    Usage:
        @rate_limit("10/minute", "login")
        def login():
            pass

        @rate_limit("100/hour", per_user=True)
        def api_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = get_rate_limiter()

            # 确定限流键
            rate_key = key
            if rate_key is None:
                rate_key = f"{request.endpoint}:{request.method}"

            # 确定标识符
            identifier = None
            if per_user and hasattr(g, 'current_user') and g.current_user:
                identifier = f"user:{g.current_user.id}"
            elif hasattr(g, 'current_user') and g.current_user:
                # 如果有用户但不是per_user，考虑用户角色
                identifier = f"{g.current_user.role.value}:{request.remote_addr}"

            # 检查限流
            if not limiter.is_allowed(rate_key, limit, identifier):
                from ..utils.responses import too_many_requests_response
                remaining = limiter.get_remaining(rate_key, limit, identifier)
                return too_many_requests_response(
                    f"请求过于频繁，请稍后再试。剩余次数: {remaining}"
                )

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# Flask应用初始化时调用
def init_rate_limit(app):
    """初始化限流功能"""
    app.config.setdefault('RATE_LIMIT_STORAGE', 'memory')
    app.config.setdefault('RATE_LIMIT_DEFAULT', '1000/hour')

    # 添加限流相关的配置
    @app.before_request
    def check_global_rate_limit():
        """检查全局限流"""
        if request.endpoint and request.endpoint.startswith('static'):
            return

        limiter = get_rate_limiter()
        user_role = None

        if hasattr(g, 'current_user') and g.current_user:
            user_role = g.current_user.role.value

        # 根据端点类型应用不同的限流规则
        if 'auth' in request.endpoint:
            limit_rule = RateLimitConfig.get_limit('login')
        elif 'api' in request.endpoint:
            limit_rule = RateLimitConfig.get_limit('api', user_role)
        elif 'upload' in request.endpoint:
            limit_rule = RateLimitConfig.get_limit('upload')
        else:
            limit_rule = app.config.get('RATE_LIMIT_DEFAULT', '1000/hour')

        if not limiter.is_allowed('global', limit_rule):
            from ..utils.responses import too_many_requests_response
            return too_many_requests_response("全局请求频率超限")


# 数据库模型（如果使用数据库存储）
class RateLimitRecord(db.Model):
    """限流记录模型"""
    __tablename__ = 'rate_limit_records'

    id = db.Column(db.Integer, primary_key=True)
    rate_key = db.Column(db.String(255), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 为提高查询性能添加复合索引
    __table_args__ = (
        db.Index('idx_rate_key_created_at', 'rate_key', 'created_at'),
    )


# 便捷函数
def check_rate_limit(key: str, limit: str = None, identifier: str = None) -> bool:
    """
    检查限流

    Args:
        key: 限流键名
        limit: 限流规则
        identifier: 标识符

    Returns:
        bool: 是否允许请求
    """
    limiter = get_rate_limiter()

    if limit is None:
        limit = RateLimitConfig.get_limit(key)

    return limiter.is_allowed(key, limit, identifier)


def get_rate_limit_info(key: str, limit: str = None, identifier: str = None) -> Dict[str, Any]:
    """
    获取限流信息

    Args:
        key: 限流键名
        limit: 限流规则
        identifier: 标识符

    Returns:
        Dict[str, Any]: 限流信息
    """
    limiter = get_rate_limiter()

    if limit is None:
        limit = RateLimitConfig.get_limit(key)

    max_requests, period_seconds = limiter._parse_limit(limit)
    remaining = limiter.get_remaining(key, limit, identifier)

    return {
        'limit': limit,
        'max_requests': max_requests,
        'period_seconds': period_seconds,
        'remaining': remaining,
        'used': max_requests - remaining,
        'reset_time': time.time() + period_seconds
    }