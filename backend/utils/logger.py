# ========================================
# 学生信息管理系统 - 日志工具类
# ========================================

import logging
import logging.handlers
import json
import os
import sys
import traceback
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from contextlib import contextmanager
from functools import wraps
import inspect

from flask import current_app, request, g


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormatter(logging.Formatter):
    """自定义日志格式器"""

    def __init__(self, include_traceback: bool = True):
        """
        初始化日志格式器

        Args:
            include_traceback: 是否包含堆栈跟踪
        """
        super().__init__()
        self.include_traceback = include_traceback

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 基础信息
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # 添加线程信息
        if hasattr(record, 'thread_id'):
            log_data['thread_id'] = record.thread_id
        else:
            log_data['thread_id'] = threading.get_ident()

        # 添加请求信息（如果在请求上下文中）
        if hasattr(request, 'endpoint'):
            log_data['request'] = {
                'method': request.method,
                'url': request.url,
                'endpoint': request.endpoint,
                'remote_addr': request.environ.get('REMOTE_ADDR')
            }

            if hasattr(g, 'current_user') and g.current_user:
                log_data['request']['user_id'] = g.current_user.id

        # 添加自定义字段
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # 添加异常信息
        if record.exc_info and self.include_traceback:
            exc_type, exc_value, exc_traceback = record.exc_info
            log_data['exception'] = {
                'type': exc_type.__name__ if exc_type else None,
                'message': str(exc_value) if exc_value else None,
                'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
            }

        # 根据格式选择输出方式
        if current_app.config.get('LOG_JSON_FORMAT', False):
            return json.dumps(log_data, ensure_ascii=False)
        else:
            return self._format_text(log_data)

    def _format_text(self, log_data: Dict[str, Any]) -> str:
        """格式化为文本"""
        parts = [
            f"[{log_data['timestamp']}]",
            f"[{log_data['level']}]",
            f"[{log_data['logger']}]",
            f"[{log_data['module']}:{log_data['function']}:{log_data['line']}]",
            log_data['message']
        ]

        if 'request' in log_data:
            request_info = log_data['request']
            parts.append(f"[{request_info['method']} {request_info.get('endpoint', 'unknown')}]")

        base_log = ' '.join(parts)

        # 添加异常信息
        if 'exception' in log_data:
            exception = log_data['exception']
            base_log += f"\nException: {exception['type']}: {exception['message']}"
            if exception['traceback']:
                base_log += f"\n{''.join(exception['traceback'])}"

        # 添加额外字段
        extra_fields = {k: v for k, v in log_data.items()
                       if k not in ['timestamp', 'level', 'logger', 'message',
                                  'module', 'function', 'line', 'request', 'exception']}

        if extra_fields:
            base_log += f" | Extra: {json.dumps(extra_fields, ensure_ascii=False)}"

        return base_log


class StructuredLogger:
    """结构化日志器"""

    def __init__(self, name: str):
        """
        初始化结构化日志器

        Args:
            name: 日志器名称
        """
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """设置日志器"""
        # 避免重复添加处理器
        if self.logger.handlers:
            return

        # 设置日志级别
        self.logger.setLevel(current_app.config.get('LOG_LEVEL', logging.INFO))

        # 创建格式器
        formatter = LogFormatter()

        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 添加文件处理器
        log_dir = current_app.config.get('LOG_DIR', 'logs')
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 主日志文件
        log_file = os.path.join(log_dir, f"{current_app.config.get('APP_NAME', 'app')}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=current_app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),  # 10MB
            backupCount=current_app.config.get('LOG_BACKUP_COUNT', 5)
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 错误日志文件
        error_log_file = os.path.join(log_dir, f"{current_app.config.get('APP_NAME', 'app')}_error.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=current_app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),
            backupCount=current_app.config.get('LOG_BACKUP_COUNT', 5)
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """错误日志"""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def _log(self, level: LogLevel, message: str, **kwargs):
        """
        记录日志

        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外字段
        """
        # 创建自定义日志记录
        record = self.logger.makeRecord(
            self.logger.name,
            level.value,
            inspect.stack()[2][1],  # 调用者文件名
            inspect.stack()[2][2],  # 调用者行号
            message,
            (),
            None
        )

        # 添加额外字段
        if kwargs:
            record.extra_fields = kwargs

        self.logger.handle(record)


class AuditLogger:
    """审计日志器"""

    def __init__(self):
        """初始化审计日志器"""
        self.logger = logging.getLogger('audit')
        self._setup_audit_logger()

    def _setup_audit_logger(self):
        """设置审计日志器"""
        if self.logger.handlers:
            return

        log_dir = current_app.config.get('LOG_DIR', 'logs')
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 审计日志文件
        audit_log_file = os.path.join(log_dir, 'audit.log')
        handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=current_app.config.get('LOG_MAX_BYTES', 50 * 1024 * 1024),  # 50MB
            backupCount=current_app.config.get('LOG_BACKUP_COUNT', 10)
        )

        # 审计日志使用JSON格式
        formatter = LogFormatter(include_traceback=False)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)

    def log_action(
        self,
        action: str,
        user_id: int = None,
        resource_type: str = None,
        resource_id: int = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        记录用户操作

        Args:
            action: 操作类型
            user_id: 用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            details: 操作详情
            ip_address: IP地址
            user_agent: 用户代理
        """
        audit_data = {
            'action': action,
            'timestamp': datetime.utcnow().isoformat()
        }

        if user_id:
            audit_data['user_id'] = user_id

        if resource_type:
            audit_data['resource_type'] = resource_type

        if resource_id:
            audit_data['resource_id'] = resource_id

        if details:
            audit_data['details'] = details

        if ip_address:
            audit_data['ip_address'] = ip_address
        elif request:
            audit_data['ip_address'] = request.environ.get('REMOTE_ADDR')

        if user_agent:
            audit_data['user_agent'] = user_agent
        elif request:
            audit_data['user_agent'] = request.headers.get('User-Agent')

        # 记录审计日志
        self.logger.info(json.dumps(audit_data, ensure_ascii=False))

    def log_login(self, user_id: int, success: bool, ip_address: str = None, reason: str = None):
        """记录登录事件"""
        action = 'login_success' if success else 'login_failed'
        details = {'success': success}

        if reason:
            details['reason'] = reason

        self.log_action(
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )

    def log_permission_check(
        self,
        user_id: int,
        permission: str,
        resource_type: str = None,
        resource_id: int = None,
        granted: bool
    ):
        """记录权限检查"""
        self.log_action(
            action='permission_check',
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={
                'permission': permission,
                'granted': granted
            }
        )

    def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int = None,
        operation: str = 'read'
    ):
        """记录数据访问"""
        self.log_action(
            action='data_access',
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={'operation': operation}
        )


class PerformanceLogger:
    """性能日志器"""

    def __init__(self):
        """初始化性能日志器"""
        self.logger = logging.getLogger('performance')
        self._setup_performance_logger()

    def _setup_performance_logger(self):
        """设置性能日志器"""
        if self.logger.handlers:
            return

        log_dir = current_app.config.get('LOG_DIR', 'logs')
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 性能日志文件
        perf_log_file = os.path.join(log_dir, 'performance.log')
        handler = logging.handlers.RotatingFileHandler(
            perf_log_file,
            maxBytes=current_app.config.get('LOG_MAX_BYTES', 20 * 1024 * 1024),  # 20MB
            backupCount=current_app.config.get('LOG_BACKUP_COUNT', 5)
        )

        formatter = LogFormatter(include_traceback=False)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)

    def log_slow_query(
        self,
        query: str,
        execution_time: float,
        parameters: List = None,
        threshold: float = 1.0
    ):
        """记录慢查询"""
        if execution_time > threshold:
            self.logger.info(
                f"Slow query detected",
                extra_fields={
                    'query': query,
                    'execution_time': execution_time,
                    'parameters': parameters,
                    'threshold': threshold
                }
            )

    def log_api_performance(
        self,
        endpoint: str,
        method: str,
        execution_time: float,
        status_code: int,
        user_id: int = None
    ):
        """记录API性能"""
        extra_fields = {
            'endpoint': endpoint,
            'method': method,
            'execution_time': execution_time,
            'status_code': status_code
        }

        if user_id:
            extra_fields['user_id'] = user_id

        level = LogLevel.WARNING if execution_time > 2.0 else LogLevel.INFO
        self._log(level, f"API call completed", **extra_fields)

    def _log(self, level: LogLevel, message: str, **kwargs):
        """记录日志"""
        record = self.logger.makeRecord(
            self.logger.name,
            level.value,
            inspect.stack()[2][1],
            inspect.stack()[2][2],
            message,
            (),
            None
        )

        if kwargs:
            record.extra_fields = kwargs

        self.logger.handle(record)


class SecurityLogger:
    """安全日志器"""

    def __init__(self):
        """初始化安全日志器"""
        self.logger = logging.getLogger('security')
        self._setup_security_logger()

    def _setup_security_logger(self):
        """设置安全日志器"""
        if self.logger.handlers:
            return

        log_dir = current_app.config.get('LOG_DIR', 'logs')
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 安全日志文件
        security_log_file = os.path.join(log_dir, 'security.log')
        handler = logging.handlers.RotatingFileHandler(
            security_log_file,
            maxBytes=current_app.config.get('LOG_MAX_BYTES', 30 * 1024 * 1024),  # 30MB
            backupCount=current_app.config.get('LOG_BACKUP_COUNT', 10)
        )

        formatter = LogFormatter(include_traceback=False)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)

    def log_suspicious_activity(
        self,
        activity_type: str,
        ip_address: str,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        """记录可疑活动"""
        extra_fields = {
            'activity_type': activity_type,
            'ip_address': ip_address
        }

        if user_id:
            extra_fields['user_id'] = user_id

        if details:
            extra_fields.update(details)

        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            extra_fields=extra_fields
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        ip_address: str = None,
        user_id: int = None
    ):
        """记录安全事件"""
        extra_fields = {
            'event_type': event_type,
            'severity': severity,
            'description': description
        }

        if ip_address:
            extra_fields['ip_address'] = ip_address

        if user_id:
            extra_fields['user_id'] = user_id

        level = LogLevel.ERROR if severity in ['high', 'critical'] else LogLevel.WARNING
        self._log(level, f"Security event: {event_type}", **extra_fields)

    def _log(self, level: LogLevel, message: str, **kwargs):
        """记录日志"""
        record = self.logger.makeRecord(
            self.logger.name,
            level.value,
            inspect.stack()[2][1],
            inspect.stack()[2][2],
            message,
            (),
            None
        )

        if kwargs:
            record.extra_fields = kwargs

        self.logger.handle(record)


# 全局日志器实例
_structured_logger = None
_audit_logger = None
_performance_logger = None
_security_logger = None


def get_structured_logger(name: str = None) -> StructuredLogger:
    """获取结构化日志器"""
    global _structured_logger
    if _structured_logger is None or name:
        _structured_logger = StructuredLogger(name or 'app')
    return _structured_logger


def get_audit_logger() -> AuditLogger:
    """获取审计日志器"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def get_performance_logger() -> PerformanceLogger:
    """获取性能日志器"""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = PerformanceLogger()
    return _performance_logger


def get_security_logger() -> SecurityLogger:
    """获取安全日志器"""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger()
    return _security_logger


# 装饰器
def log_execution_time(logger: StructuredLogger = None, threshold: float = None):
    """
    记录函数执行时间的装饰器

    Args:
        logger: 日志器实例
        threshold: 时间阈值（秒），超过则记录警告

    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            start_time = time.time()

            try:
                result = f(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                log_message = f"Function {f.__name__} executed in {execution_time:.4f}s"

                log_instance = logger or get_structured_logger()

                if threshold and execution_time > threshold:
                    log_instance.warning(log_message, execution_time=execution_time)
                else:
                    log_instance.info(log_message, execution_time=execution_time)

        return decorated_function
    return decorator


def log_api_call():
    """记录API调用的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            start_time = time.time()
            perf_logger = get_performance_logger()

            try:
                result = f(*args, **kwargs)
                status_code = 200
                if isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                execution_time = time.time() - start_time
                perf_logger.log_api_performance(
                    endpoint=request.endpoint,
                    method=request.method,
                    execution_time=execution_time,
                    status_code=status_code,
                    user_id=getattr(g, 'current_user', {}).get('id')
                )

        return decorated_function
    return decorator


@contextmanager
def log_context(**context):
    """
    日志上下文管理器

    Args:
        **context: 上下文信息
    """
    # 保存原始的上下文
    original_context = getattr(g, 'log_context', {})

    # 设置新的上下文
    g.log_context = {**original_context, **context}

    try:
        yield
    finally:
        # 恢复原始上下文
        g.log_context = original_context


def log_exception(logger: StructuredLogger = None):
    """
    异常日志装饰器

    Args:
        logger: 日志器实例

    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log_instance = logger or get_structured_logger()
                log_instance.error(
                    f"Exception in {f.__name__}: {str(e)}",
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    traceback=traceback.format_exc()
                )
                raise

        return decorated_function
    return decorator


# 便捷函数
def log_user_action(action: str, resource_type: str = None, resource_id: int = None, details: Dict = None):
    """记录用户操作（便捷函数）"""
    audit_logger = get_audit_logger()
    user_id = getattr(g, 'current_user', {}).get('id')
    audit_logger.log_action(action, user_id, resource_type, resource_id, details)


def log_error(message: str, **kwargs):
    """记录错误（便捷函数）"""
    logger = get_structured_logger()
    logger.error(message, **kwargs)


def log_info(message: str, **kwargs):
    """记录信息（便捷函数）"""
    logger = get_structured_logger()
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告（便捷函数）"""
    logger = get_structured_logger()
    logger.warning(message, **kwargs)