# ========================================
# 学生信息管理系统 - 缓存工具类
# ========================================

import json
import pickle
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from collections import OrderedDict
import hashlib

from flask import current_app


class CacheBackend:
    """缓存后端基类"""

    def get(self, key: str) -> Any:
        """获取缓存值"""
        raise NotImplementedError

    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """删除缓存"""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        raise NotImplementedError

    def clear(self) -> bool:
        """清空所有缓存"""
        raise NotImplementedError

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键"""
        raise NotImplementedError

    def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        raise NotImplementedError

    def expire(self, key: str, timeout: int) -> bool:
        """设置过期时间"""
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """内存缓存"""

    def __init__(self, max_size: int = 10000):
        """
        初始化内存缓存

        Args:
            max_size: 最大缓存项数
        """
        self.cache = OrderedDict()
        self.expiry_times = {}
        self.max_size = max_size
        self.lock = threading.Lock()

    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key in self.expiry_times:
            return time.time() > self.expiry_times[key]
        return False

    def _cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self.expiry_times.items()
            if current_time > expiry_time
        ]

        for key in expired_keys:
            self.cache.pop(key, None)
            del self.expiry_times[key]

    def _evict_if_needed(self):
        """如果需要，驱逐最旧的缓存项"""
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

    def get(self, key: str) -> Any:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                return None

            if self._is_expired(key):
                self.cache.pop(key, None)
                del self.expiry_times[key]
                return None

            # 移动到末尾（LRU）
            value = self.cache.pop(key)
            self.cache[key] = value
            return value

    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        try:
            with self.lock:
                self._cleanup_expired()
                self._evict_if_needed()

                self.cache[key] = value

                if timeout is not None:
                    self.expiry_times[key] = time.time() + timeout
                elif key in self.expiry_times:
                    del self.expiry_times[key]

                return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            with self.lock:
                self.cache.pop(key, None)
                self.expiry_times.pop(key, None)
                return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        with self.lock:
            if key not in self.cache:
                return False

            if self._is_expired(key):
                self.cache.pop(key, None)
                del self.expiry_times[key]
                return False

            return True

    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            with self.lock:
                self.cache.clear()
                self.expiry_times.clear()
                return True
        except Exception:
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键"""
        with self.lock:
            self._cleanup_expired()

            if pattern == "*":
                return list(self.cache.keys())

            # 简单的通配符匹配
            import fnmatch
            return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]

    def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        with self.lock:
            if key in self.cache and not self._is_expired(key):
                try:
                    current_value = int(self.cache[key])
                    new_value = current_value + amount
                    self.cache[key] = new_value
                    return new_value
                except (ValueError, TypeError):
                    pass

            self.cache[key] = amount
            return amount

    def expire(self, key: str, timeout: int) -> bool:
        """设置过期时间"""
        with self.lock:
            if key in self.cache:
                self.expiry_times[key] = time.time() + timeout
                return True
            return False


class RedisCache(CacheBackend):
    """Redis缓存"""

    def __init__(self):
        """初始化Redis缓存"""
        try:
            from extensions import cache
            self.redis_client = cache
        except ImportError:
            raise ImportError("需要安装Redis: pip install redis")

    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return str(value).encode('utf-8')
            else:
                return pickle.dumps(value)
        except Exception:
            return pickle.dumps(value)

    def _deserialize(self, value: bytes) -> Any:
        """反序列化值"""
        try:
            # 尝试反序列化为字符串
            decoded = value.decode('utf-8')
            # 尝试转换为数字
            try:
                if '.' in decoded:
                    return float(decoded)
                return int(decoded)
            except ValueError:
                return decoded
        except (UnicodeDecodeError, AttributeError):
            # 使用pickle反序列化
            try:
                return pickle.loads(value)
            except Exception:
                return value.decode('utf-8', errors='ignore')

    def get(self, key: str) -> Any:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value is not None:
                return self._deserialize(value)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        try:
            serialized_value = self._serialize(value)
            if timeout is not None:
                return self.redis_client.set(key, serialized_value, ex=timeout)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False

    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            return bool(self.redis_client.flushdb())
        except Exception:
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键"""
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception:
            return []

    def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        try:
            return self.redis_client.incr(key, amount)
        except Exception:
            return 0

    def expire(self, key: str, timeout: int) -> bool:
        """设置过期时间"""
        try:
            return bool(self.redis_client.expire(key, timeout))
        except Exception:
            return False


class CacheManager:
    """缓存管理器"""

    def __init__(self, backend: str = 'memory'):
        """
        初始化缓存管理器

        Args:
            backend: 缓存后端 ('memory', 'redis')
        """
        self.backend = self._get_backend(backend)

    def _get_backend(self, backend: str) -> CacheBackend:
        """获取缓存后端"""
        if backend == 'memory':
            return MemoryCache()
        elif backend == 'redis':
            return RedisCache()
        else:
            raise ValueError(f"不支持的缓存后端: {backend}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        value = self.backend.get(key)
        return value if value is not None else default

    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        if timeout is None:
            timeout = current_app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        return self.backend.set(key, value, timeout)

    def get_or_set(
        self,
        key: str,
        fallback_func: Callable,
        timeout: int = None,
        *args,
        **kwargs
    ) -> Any:
        """
        获取缓存，如果不存在则调用回退函数

        Args:
            key: 缓存键
            fallback_func: 回退函数
            timeout: 超时时间
            *args: 回退函数参数
            **kwargs: 回退函数关键字参数

        Returns:
            Any: 缓存值或函数返回值
        """
        value = self.get(key)
        if value is not None:
            return value

        # 计算新值
        computed_value = fallback_func(*args, **kwargs)
        self.set(key, computed_value, timeout)
        return computed_value

    def delete(self, key: str) -> bool:
        """删除缓存"""
        return self.backend.delete(key)

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.backend.exists(key)

    def clear(self) -> bool:
        """清空所有缓存"""
        return self.backend.clear()

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键"""
        return self.backend.keys(pattern)

    def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        keys = self.keys(pattern)
        deleted_count = 0
        for key in keys:
            if self.delete(key):
                deleted_count += 1
        return deleted_count

    def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        return self.backend.increment(key, amount)

    def expire(self, key: str, timeout: int) -> bool:
        """设置过期时间"""
        return self.backend.expire(key, timeout)

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, mapping: Dict[str, Any], timeout: int = None) -> int:
        """批量设置缓存"""
        success_count = 0
        for key, value in mapping.items():
            if self.set(key, value, timeout):
                success_count += 1
        return success_count

    def delete_many(self, keys: List[str]) -> int:
        """批量删除缓存"""
        success_count = 0
        for key in keys:
            if self.delete(key):
                success_count += 1
        return success_count


class CacheDecorator:
    """缓存装饰器"""

    def __init__(self, cache_manager: CacheManager):
        """
        初始化缓存装饰器

        Args:
            cache_manager: 缓存管理器
        """
        self.cache_manager = cache_manager

    def cached(
        self,
        timeout: int = None,
        key_prefix: str = None,
        unless: Callable = None,
        make_cache_key: Callable = None
    ):
        """
        缓存装饰器

        Args:
            timeout: 缓存超时时间
            key_prefix: 键前缀
            unless: 条件函数，返回True时不缓存
            make_cache_key: 自定义缓存键生成函数

        Returns:
           装饰器函数
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 检查unless条件
                if unless and unless(*args, **kwargs):
                    return f(*args, **kwargs)

                # 生成缓存键
                if make_cache_key:
                    cache_key = make_cache_key(*args, **kwargs)
                else:
                    cache_key = self._make_cache_key(f, key_prefix, *args, **kwargs)

                # 尝试从缓存获取
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # 执行函数并缓存结果
                result = f(*args, **kwargs)
                self.cache_manager.set(cache_key, result, timeout)
                return result

            return decorated_function
        return decorator

    def cache_property(self, timeout: int = None, key_prefix: str = None):
        """
        缓存属性装饰器

        Args:
            timeout: 缓存超时时间
            key_prefix: 键前缀

        Returns:
            属性描述符
        """
        class CachedProperty:
            def __init__(self, fget):
                self.fget = fget
                self.__name__ = fget.__name__
                self.__doc__ = fget.__doc__

            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self

                cache_key = f"{key_prefix or self.__name__}:{id(obj)}"
                cached_value = self.cache_manager.get(cache_key)

                if cached_value is not None:
                    return cached_value

                value = self.fget(obj)
                self.cache_manager.set(cache_key, value, timeout)
                return value

        return CachedProperty

    def _make_cache_key(self, f, key_prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 使用函数名和参数生成哈希
        key_data = {
            'function': f.__name__,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }

        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        prefix = key_prefix or f"cache:{f.__module__}.{f.__name__}"
        return f"{prefix}:{key_hash}"


class CacheUtils:
    """缓存工具类"""

    @staticmethod
    def make_user_cache_key(user_id: int, action: str, *args) -> str:
        """生成用户相关缓存键"""
        key_parts = ['user', str(user_id), action]
        key_parts.extend(str(arg) for arg in args)
        return ':'.join(key_parts)

    @staticmethod
    def make_query_cache_key(table: str, query_params: Dict[str, Any]) -> str:
        """生成查询缓存键"""
        # 对查询参数排序以确保一致性
        sorted_params = sorted(query_params.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()

        return f"query:{table}:{params_hash}"

    @staticmethod
    def make_permission_cache_key(user_id: int, permission: str, resource_id: int = None) -> str:
        """生成权限缓存键"""
        key_parts = ['permission', str(user_id), permission]
        if resource_id is not None:
            key_parts.append(str(resource_id))
        return ':'.join(key_parts)

    @staticmethod
    def invalidate_user_cache(user_id: int) -> List[str]:
        """失效用户相关缓存"""
        pattern = f"user:{user_id}:*"
        cache_manager = get_cache_manager()
        keys = cache_manager.keys(pattern)
        cache_manager.delete_pattern(pattern)
        return keys

    @staticmethod
    def warm_up_cache(warm_up_funcs: List[Callable]) -> Dict[str, Any]:
        """预热缓存"""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for func in warm_up_funcs:
            try:
                func()
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{func.__name__}: {str(e)}")

        return results


# 全局缓存管理器实例
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器"""
    global _cache_manager
    if _cache_manager is None:
        backend = current_app.config.get('CACHE_TYPE', 'memory')
        _cache_manager = CacheManager(backend)
    return _cache_manager


def cache(timeout: int = None, key_prefix: str = None, unless: Callable = None):
    """
    缓存装饰器（便捷函数）

    Args:
        timeout: 缓存超时时间
        key_prefix: 键前缀
        unless: 条件函数

    Returns:
        装饰器函数
    """
    cache_manager = get_cache_manager()
    decorator = CacheDecorator(cache_manager)
    return decorator.cached(timeout=timeout, key_prefix=key_prefix, unless=unless)


def cache_result(key: str, timeout: int = None):
    """
    缓存结果装饰器（使用固定键）

    Args:
        key: 缓存键
        timeout: 超时时间

    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(key)

            if cached_result is not None:
                return cached_result

            result = f(*args, **kwargs)
            cache_manager.set(key, result, timeout)
            return result

        return decorated_function
    return decorator


def cached_query(timeout: int = 300):
    """
    查询缓存装饰器

    Args:
        timeout: 缓存超时时间

    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成查询缓存键
            query_params = kwargs
            cache_key = CacheUtils.make_query_cache_key(
                f.__name__,
                query_params
            )

            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(cache_key)

            if cached_result is not None:
                return cached_result

            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            return result

        return decorated_function
    return decorator