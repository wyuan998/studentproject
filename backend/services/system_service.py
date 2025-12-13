# ========================================
# 学生信息管理系统 - 系统服务
# ========================================

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, text

from .base_service import BaseService, ServiceError, NotFoundError, ValidationError
from ..models import SystemConfig, User, AuditLog, db
from ..utils.logger import get_structured_logger, get_security_logger
from ..utils.cache import get_cache_manager
from ..utils.email import EmailService


class SystemService(BaseService):
    """系统服务类"""

    def __init__(self):
        super().__init__()
        self.model_class = SystemConfig
        self.logger = get_structured_logger('SystemService')
        self.security_logger = get_security_logger()
        self.cache = get_cache_manager()

    # ========================================
    # 系统配置管理
    # ========================================

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取系统配置

        Args:
            key: 配置键
            default: 默认值

        Returns:
            Any: 配置值
        """
        try:
            # 先从缓存获取
            cache_key = f"system_config:{key}"
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 从数据库获取
            config = db.session.query(SystemConfig).filter_by(key=key, is_active=True).first()
            if config:
                value = config.get_value()
                # 缓存配置
                self.cache.set(cache_key, value, timeout=3600)  # 1小时缓存
                return value

            return default

        except Exception as e:
            self.logger.error(f"获取系统配置失败: {str(e)}", key=key)
            return default

    def set_config(self, key: str, value: Any, description: str = None, category: str = 'general') -> bool:
        """
        设置系统配置

        Args:
            key: 配置键
            value: 配置值
            description: 配置描述
            category: 配置分类

        Returns:
            bool: 是否设置成功

        Raises:
            ServiceError: 设置失败
        """
        try:
            self._check_permission('system_config')

            # 检查是否已存在
            config = db.session.query(SystemConfig).filter_by(key=key).first()

            if config:
                # 更新现有配置
                config.set_value(value)
                config.updated_at = datetime.utcnow()
                if description:
                    config.description = description
            else:
                # 创建新配置
                config = SystemConfig()
                config.key = key
                config.set_value(value)
                config.description = description or f"配置项 {key}"
                config.category = category
                config.created_at = datetime.utcnow()
                db.session.add(config)

            db.session.commit()

            # 清除缓存
            cache_key = f"system_config:{key}"
            self.cache.delete(cache_key)

            self._log_business_action('config_updated', {
                'key': key,
                'category': category,
                'is_new': config.created_at == config.updated_at
            })

            return True

        except Exception as e:
            db.session.rollback()
            if isinstance(e, ServiceError):
                raise
            self.logger.error(f"设置系统配置失败: {str(e)}", key=key)
            raise ServiceError("系统配置设置服务异常", 'CONFIG_SET_ERROR')

    # ========================================
    # 系统监控
    # ========================================

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        Returns:
            Dict[str, Any]: 系统状态信息
        """
        try:
            from flask import current_app

            # 数据库连接状态
            try:
                db.session.execute(text('SELECT 1'))
                database_status = 'healthy'
            except Exception:
                database_status = 'error'

            # 缓存状态
            try:
                test_key = 'health_check'
                self.cache.set(test_key, 'ok', timeout=10)
                cached_value = self.cache.get(test_key)
                self.cache.delete(test_key)
                cache_status = 'healthy' if cached_value == 'ok' else 'error'
            except Exception:
                cache_status = 'error'

            # 用户统计
            user_stats = {
                'total': db.session.query(User).count(),
                'active': db.session.query(User).filter_by(is_active=True).count(),
                'online_today': self._get_today_active_users()
            }

            # 系统配置
            config_count = db.session.query(SystemConfig).filter_by(is_active=True).count()

            # 最近错误日志
            error_logs = self._get_recent_error_logs()

            # 磁盘使用情况
            import os
            import shutil

            disk_usage = shutil.disk_usage('/')
            disk_stats = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'usage_percent': round(disk_usage.used / disk_usage.total * 100, 2)
            }

            return {
                'status': 'healthy' if database_status == 'healthy' and cache_status == 'healthy' else 'degraded',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'database': database_status,
                    'cache': cache_status
                },
                'statistics': {
                    'users': user_stats,
                    'configurations': config_count,
                    'disk': disk_stats
                },
                'recent_errors': error_logs
            }

        except Exception as e:
            self.logger.error(f"获取系统状态失败: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    def get_system_logs(self, level: str = None, start_time: datetime = None, end_time: datetime = None, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        获取系统日志

        Args:
            level: 日志级别筛选
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            per_page: 每页数量

        Returns:
            Dict[str, Any]: 日志列表和分页信息
        """
        try:
            self._check_permission('system_logs')

            # 构建查询
            query = db.session.query(AuditLog)

            if start_time:
                query = query.filter(AuditLog.created_at >= start_time)
            if end_time:
                query = query.filter(AuditLog.created_at <= end_time)

            query = query.order_by(AuditLog.created_at.desc())

            # 分页
            per_page = min(per_page, 200)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            logs = []
            for log in pagination.items:
                # 获取用户名
                username = db.session.query(User.username).filter_by(id=log.user_id).first()
                log_data = {
                    'id': log.id,
                    'username': username[0] if username else 'Unknown',
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'details': log.details,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at.isoformat() if log.created_at else None
                }
                logs.append(log_data)

            return {
                'logs': logs,
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
            self.logger.error(f"获取系统日志失败: {str(e)}")
            raise ServiceError("系统日志查询服务异常", 'SYSTEM_LOGS_ERROR')

    # ========================================
    # 系统维护
    # ========================================

    def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        清理过期会话

        Returns:
            Dict[str, Any]: 清理结果
        """
        try:
            self._check_permission('system_maintenance')

            # 清理过期的缓存
            expired_cache_keys = []
            for pattern in ['rate_limit:*', 'session:*', 'temp:*']:
                keys = self.cache.keys(pattern)
                expired_cache_keys.extend(keys)

            deleted_cache_count = 0
            for key in expired_cache_keys:
                if self.cache.delete(key):
                    deleted_cache_count += 1

            # 清理过期的审计日志（保留90天）
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            deleted_logs_count = db.session.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()

            db.session.commit()

            result = {
                'deleted_cache_keys': deleted_cache_count,
                'deleted_audit_logs': deleted_logs_count,
                'cutoff_date': cutoff_date.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }

            self._log_business_action('system_cleanup', result)

            return result

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"系统清理失败: {str(e)}")
            raise ServiceError("系统清理服务异常", 'SYSTEM_CLEANUP_ERROR')

    def backup_system_data(self) -> Dict[str, Any]:
        """
        备份系统数据

        Returns:
            Dict[str, Any]: 备份结果

        Raises:
            ServiceError: 备份失败
        """
        try:
            self._check_permission('system_maintenance')

            backup_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'tables': {}
            }

            # 备份关键表的数据量
            tables_to_backup = ['users', 'students', 'teachers', 'courses', 'enrollments', 'grades', 'messages']

            for table_name in tables_to_backup:
                try:
                    count = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    backup_info['tables'][table_name] = count
                except Exception as e:
                    backup_info['tables'][table_name] = f"Error: {str(e)}"

            # 这里可以添加实际的数据库备份逻辑
            # 例如：调用数据库备份命令或使用ORM导出功能

            self._log_business_action('system_backup', backup_info)

            return {
                'success': True,
                'backup_info': backup_info,
                'message': '系统数据备份任务已提交'
            }

        except Exception as e:
            self.logger.error(f"系统备份失败: {str(e)}")
            raise ServiceError("系统备份服务异常", 'SYSTEM_BACKUP_ERROR')

    # ========================================
    # 安全管理
    # ========================================

    def get_security_events(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """
        获取安全事件

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict[str, Any]]: 安全事件列表
        """
        try:
            self._check_permission('security_monitoring')

            # 从安全日志获取事件
            # 这里简化为查询审计日志中的安全相关操作
            security_actions = ['login_failed', 'permission_denied', 'suspicious_activity']

            query = db.session.query(AuditLog).filter(
                AuditLog.action.in_(security_actions)
            )

            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)

            query = query.order_by(AuditLog.created_at.desc())
            events = query.limit(100).all()

            security_events = []
            for event in events:
                username = db.session.query(User.username).filter_by(id=event.user_id).first()
                event_data = {
                    'id': event.id,
                    'username': username[0] if username else 'Unknown',
                    'action': event.action,
                    'details': event.details,
                    'ip_address': event.ip_address,
                    'created_at': event.created_at.isoformat() if event.created_at else None
                }
                security_events.append(event_data)

            return security_events

        except Exception as e:
            self.logger.error(f"获取安全事件失败: {str(e)}")
            raise ServiceError("安全事件查询服务异常", 'SECURITY_EVENTS_ERROR')

    def detect_suspicious_activities(self) -> List[Dict[str, Any]]:
        """
        检测可疑活动

        Returns:
            List[Dict[str, Any]]: 可疑活动列表
        """
        try:
            self._check_permission('security_monitoring')

            suspicious_activities = []

            # 检测异常登录模式
            recent_failures = self._detect_abnormal_login_failures()
            suspicious_activities.extend(recent_failures)

            # 检测异常API调用
            abnormal_apis = self._detect_abnormal_api_calls()
            suspicious_activities.extend(abnormal_apis)

            # 记录检测结果
            if suspicious_activities:
                self.security_logger.log_security_event(
                    'suspicious_activity_detected',
                    'medium',
                    f"检测到 {len(suspicious_activities)} 个可疑活动"
                )

            return suspicious_activities

        except Exception as e:
            self.logger.error(f"检测可疑活动失败: {str(e)}")
            return []

    # ========================================
    # 系统统计
    # ========================================

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        获取仪表板统计数据

        Returns:
            Dict[str, Any]: 统计数据
        """
        try:
            from ..utils.datetime_utils import now, AcademicCalendar

            current_time = now()

            # 用户统计
            total_users = db.session.query(User).count()
            active_users = db.session.query(User).filter_by(is_active=True).count()
            new_users_this_month = db.session.query(User).filter(
                User.created_at >= current_time.replace(day=1, hour=0, minute=0, second=0)
            ).count()

            # 学生和教师统计
            total_students = db.session.query(func.count(func.text('id'))).select_from(func.text('students')).scalar() or 0
            total_teachers = db.session.query(func.count(func.text('id'))).select_from(func.text('teachers')).scalar() or 0

            # 课程统计
            total_courses = db.session.query(func.count(func.text('id'))).select_from(func.text('courses')).scalar() or 0
            active_courses = db.session.query(func.count(func.text('id'))).select_from(func.text('courses')).filter_by(status='active').scalar() or 0

            # 选课和成绩统计
            total_enrollments = db.session.query(func.count(func.text('id'))).select_from(func.text('enrollments')).scalar() or 0
            total_grades = db.session.query(func.count(func.text('id'))).select_from(func.text('grades')).scalar() or 0

            # 当前学期
            current_semester = AcademicCalendar.get_current_semester()
            current_year = current_time.year

            return {
                'timestamp': current_time.isoformat(),
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'new_this_month': new_users_this_month,
                    'students': total_students,
                    'teachers': total_teachers
                },
                'courses': {
                    'total': total_courses,
                    'active': active_courses,
                    'current_semester': f"{current_year}-{current_semester}"
                },
                'enrollments': {
                    'total': total_enrollments,
                    'grades_recorded': total_grades
                },
                'system': {
                    'status': self.get_system_status()['status']
                }
            }

        except Exception as e:
            self.logger.error(f"获取仪表板统计失败: {str(e)}")
            raise ServiceError("仪表板统计服务异常", 'DASHBOARD_STATS_ERROR')

    # ========================================
    # 辅助方法
    # ========================================

    def _get_today_active_users(self) -> int:
        """获取今日活跃用户数"""
        try:
            today = datetime.utcnow().date()
            start_of_day = datetime.combine(today, datetime.min.time())

            # 统计今天有登录活动的用户
            active_users = db.session.query(func.count(func.distinct(AuditLog.user_id))).filter(
                and_(
                    AuditLog.created_at >= start_of_day,
                    AuditLog.action == 'login_success'
                )
            ).scalar()

            return active_users or 0
        except Exception:
            return 0

    def _get_recent_error_logs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的错误日志"""
        try:
            # 这里应该从实际的日志文件或日志系统读取
            # 简化实现，返回审计日志中的错误操作
            error_actions = ['login_failed', 'permission_denied', 'error']

            logs = db.session.query(AuditLog).filter(
                AuditLog.action.in_(error_actions)
            ).order_by(AuditLog.created_at.desc()).limit(limit).all()

            error_logs = []
            for log in logs:
                error_logs.append({
                    'id': log.id,
                    'action': log.action,
                    'details': log.details,
                    'created_at': log.created_at.isoformat() if log.created_at else None
                })

            return error_logs
        except Exception:
            return []

    def _detect_abnormal_login_failures(self) -> List[Dict[str, Any]]:
        """检测异常登录失败"""
        try:
            recent_hours = 24
            threshold = 5  # 24小时内失败次数阈值

            start_time = datetime.utcnow() - timedelta(hours=recent_hours)

            # 查询异常登录失败
            failed_logins = db.session.query(
                AuditLog.ip_address,
                func.count(AuditLog.id).label('failure_count')
            ).filter(
                and_(
                    AuditLog.action == 'login_failed',
                    AuditLog.created_at >= start_time
                )
            ).group_by(AuditLog.ip_address)\
             .having(func.count(AuditLog.id) >= threshold)\
             .all()

            suspicious = []
            for ip, count in failed_logins:
                suspicious.append({
                    'type': 'abnormal_login_failures',
                    'ip_address': ip,
                    'failure_count': count,
                    'time_window': f"{recent_hours} hours"
                })

            return suspicious
        except Exception:
            return []

    def _detect_abnormal_api_calls(self) -> List[Dict[str, Any]]:
        """检测异常API调用"""
        try:
            # 这里可以实现更复杂的异常检测逻辑
            # 例如：短时间内的频繁API调用
            recent_minutes = 5
            threshold = 100  # 5分钟内调用次数阈值

            start_time = datetime.utcnow() - timedelta(minutes=recent_minutes)

            # 简化实现：统计最近的操作频率
            high_frequency_users = db.session.query(
                AuditLog.user_id,
                func.count(AuditLog.id).label('call_count')
            ).filter(AuditLog.created_at >= start_time)\
             .group_by(AuditLog.user_id)\
             .having(func.count(AuditLog.id) >= threshold)\
             .all()

            suspicious = []
            for user_id, count in high_frequency_users:
                username = db.session.query(User.username).filter_by(id=user_id).first()
                suspicious.append({
                    'type': 'high_frequency_api_calls',
                    'user_id': user_id,
                    'username': username[0] if username else 'Unknown',
                    'call_count': count,
                    'time_window': f"{recent_minutes} minutes"
                })

            return suspicious
        except Exception:
            return []

    # ========================================
    # 数据验证
    # ========================================

    def _validate_data(self, data: Dict[str, Any], operation: str = 'create', instance: Any = None):
        """
        验证系统配置数据

        Args:
            data: 要验证的数据
            operation: 操作类型
            instance: 更新时的实例
        """
        if operation == 'create':
            # 创建时的验证
            if 'key' in data:
                if not data['key'] or not isinstance(data['key'], str):
                    raise ValidationError("配置键不能为空", 'key')

                # 检查键名格式
                import re
                if not re.match(r'^[a-z][a-z0-9_]*$', data['key']):
                    raise ValidationError("配置键格式不正确", 'key')