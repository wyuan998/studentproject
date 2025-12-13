# ========================================
# 学生信息管理系统 - 装饰器工具
# ========================================

from functools import wraps
from flask import request, g, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import time

from utils.responses import forbidden_response, unauthorized_response, error_response
from utils.rate_limit import rate_limiter

def require_permission(permission):
    """
    权限检查装饰器

    Args:
        permission (str): 所需权限名称

    Usage:
        @require_permission('user_management')
        def sensitive_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not hasattr(g, 'current_user'):
                from models import User
                g.current_user = User.query.get(current_user_id)

            if not g.current_user:
                return unauthorized_response("用户不存在")

            if not g.current_user.is_active():
                return forbidden_response("用户已被禁用")

            if not g.current_user.has_permission(permission):
                return forbidden_response("权限不足")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role):
    """
    角色检查装饰器

    Args:
        role (str): 所需角色名称

    Usage:
        @require_role('admin')
        def admin_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not hasattr(g, 'current_user'):
                from models import User
                g.current_user = User.query.get(current_user_id)

            if not g.current_user or g.current_user.role.value != role:
                return forbidden_response(f"需要{role}角色")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_any_role(*roles):
    """
    多角色检查装饰器（满足其中一个即可）

    Args:
        roles (list): 可接受的角色列表

    Usage:
        @require_any_role('admin', 'teacher')
        def multi_role_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not hasattr(g, 'current_user'):
                from models import User
                g.current_user = User.query.get(current_user_id)

            if not g.current_user or g.current_user.role.value not in roles:
                return forbidden_response(f"需要以下角色之一: {', '.join(roles)}")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_self_or_permission(permission):
    """
    要求是用户本人或有特定权限

    Args:
        permission (str): 所需权限名称

    Usage:
        @require_self_or_permission('user_management')
        def update_user_profile(user_id):
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            # 从参数中获取用户ID
            user_id = kwargs.get('user_id') or request.view_args.get('user_id')

            # 检查是否是本人
            is_self = user_id == current_user_id

            # 检查是否有权限
            if not hasattr(g, 'current_user'):
                from models import User
                g.current_user = User.query.get(current_user_id)

            if not g.current_user:
                return unauthorized_response("用户不存在")

            has_permission = g.current_user.has_permission(permission)

            if not (is_self or has_permission):
                return forbidden_response("权限不足")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """管理员权限装饰器"""
    return require_role('admin')(f)

def teacher_required(f):
    """教师权限装饰器"""
    return require_role('teacher')(f)

def student_required(f):
    """学生权限装饰器"""
    return require_role('student')(f)

def rate_limit(limit):
    """
    限流装饰器

    Args:
        limit (str): 限流规则，如 "10/minute", "100/hour"

    Usage:
        @rate_limit("10/minute")
        def limited_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 使用限流器检查
            if not rate_limiter.is_allowed(request.endpoint, limit):
                return error_response("请求过于频繁，请稍后再试", 429, 'TOO_MANY_REQUESTS')

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout=300):
    """
    缓存响应装饰器

    Args:
        timeout (int): 缓存超时时间（秒）

    Usage:
        @cache_response(timeout=60)
        def cached_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = f"response:{request.endpoint}:{hash(str(request.args))}"

            # 尝试从缓存获取
            from extensions import cache
            cached_response = cache.get(cache_key)

            if cached_response:
                return cached_response

            # 执行函数并缓存结果
            response = f(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout)

            return response
        return decorated_function
    return decorator

def validate_json(schema_class):
    """
    JSON数据验证装饰器

    Args:
        schema_class: Marshmallow Schema类

    Usage:
        @validate_json(UserCreateSchema)
        def create_user():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                schema = schema_class()
                data = schema.load(request.json)
                g.validated_data = data
                return f(*args, **kwargs)
            except Exception as e:
                from utils.responses import validation_error_response
                return validation_error_response({'validation': str(e)})
        return decorated_function
    return decorator

def log_api_call():
    """
    API调用日志装饰器

    Usage:
        @log_api_call()
        def api_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            try:
                response = f(*args, **kwargs)

                # 记录成功日志
                duration = time.time() - start_time
                current_app.logger.info(
                    f"API Call: {request.method} {request.endpoint} - "
                    f"Status: {response[1] if isinstance(response, tuple) else 200} - "
                    f"Duration: {duration:.3f}s"
                )

                return response

            except Exception as e:
                # 记录错误日志
                duration = time.time() - start_time
                current_app.logger.error(
                    f"API Call Failed: {request.method} {request.endpoint} - "
                    f"Error: {str(e)} - "
                    f"Duration: {duration:.3f}s"
                )
                raise

        return decorated_function
    return decorator

def timing_decorator():
    """
    性能计时装饰器

    Usage:
        @timing_decorator()
        def timed_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()

            current_app.logger.info(
                f"Function {f.__name__} executed in {end_time - start_time:.4f} seconds"
            )

            return result
        return decorated_function
    return decorator

def transactional():
    """
    数据库事务装饰器

    Usage:
        @transactional()
        def db_operation():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from extensions import db

            try:
                result = f(*args, **kwargs)
                db.session.commit()
                return result
            except Exception as e:
                db.session.rollback()
                raise

        return decorated_function
    return decorator

def handle_errors():
    """
    错误处理装饰器

    Usage:
        @handle_errors()
        def error_prone_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                return error_response(str(e), 400)
            except KeyError as e:
                return error_response(f"缺少必需参数: {str(e)}", 400)
            except PermissionError as e:
                return forbidden_response(str(e))
            except FileNotFoundError as e:
                return not_found_response(str(e))
            except Exception as e:
                current_app.logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
                return error_response("服务器内部错误", 500)

        return decorated_function
    return decorator

def conditional(condition_decorator):
    """
    条件装饰器 - 根据条件决定是否应用装饰器

    Args:
        condition_decorator: 条件装饰器函数

    Usage:
        @conditional(lambda: debug_mode)
        def debug_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if condition_decorator():
                # 应用装饰器
                return condition_decorator(f)(*args, **kwargs)
            else:
                # 不应用装饰器
                return f(*args, **kwargs)
        return decorated_function
    return decorator

def class_method_decorator(decorator):
    """
    类方法装饰器

    Args:
        decorator: 要应用的装饰器

    Usage:
        @class_method_decorator(rate_limit("10/minute"))
        class MyClass:
            @classmethod
            def my_class_method(cls):
                pass
    """
    def decorate(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls
    return decorate

def retry(max_attempts=3, delay=1, backoff=2):
    """
    重试装饰器

    Args:
        max_attempts (int): 最大重试次数
        delay (float): 初始延迟时间（秒）
        backoff (float): 延迟倍数

    Usage:
        @retry(max_attempts=3, delay=1)
        def unreliable_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            attempts = 0
            current_delay = delay

            while attempts < max_attempts:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise

                    current_app.logger.warning(
                        f"Function {f.__name__} failed (attempt {attempts}/{max_attempts}): {str(e)}"
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

        return decorated_function
    return decorator

def async_task(celery_app):
    """
    异步任务装饰器

    Args:
        celery_app: Celery应用实例

    Usage:
        @async_task(celery)
        def background_task():
            pass
    """
    def decorator(f):
        return celery_app.task(f)
    return decorator