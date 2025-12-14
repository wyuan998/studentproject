# ========================================
# 隐私保护工具
# ========================================

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PrivacyFilter:
    """隐私数据过滤器"""

    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """
        脱敏手机号码
        例: 13812345678 -> 138****5678
        """
        if not phone or len(phone) < 11:
            return phone

        return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', phone)

    @staticmethod
    def mask_email(email: str) -> str:
        """
        脱敏邮箱地址
        例: user@example.com -> u***@example.com
        """
        if not email or '@' not in email:
            return email

        local, domain = email.split('@', 1)
        if len(local) <= 1:
            return f"{local}@{domain}"

        return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"

    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """
        脱敏身份证号
        例: 110101199001011234 -> 110101********1234
        """
        if not id_card or len(id_card) < 10:
            return id_card

        return re.sub(r'(\d{6})\d{8}(\d{4})', r'\1********\2', id_card)

    @staticmethod
    def mask_address(address: str, visible_chars: int = 6) -> str:
        """
        脱敏地址信息
        只显示前visible_chars个字符，其余用*代替
        """
        if not address or len(address) <= visible_chars:
            return address

        return address[:visible_chars] + '***'

    @staticmethod
    def mask_name(name: str) -> str:
        """
        脱敏姓名
        例: 张三 -> 张*
        """
        if not name or len(name) <= 1:
            return name

        return name[0] + '*' * (len(name) - 1)

    @staticmethod
    def filter_user_data(user_data: Dict[str, Any],
                        viewer_role: str = 'self',
                        include_sensitive: bool = False) -> Dict[str, Any]:
        """
        根据查看者角色过滤用户数据

        Args:
            user_data: 用户原始数据
            viewer_role: 查看者角色 (self/teacher/admin/stranger)
            include_sensitive: 是否包含敏感信息

        Returns:
            过滤后的用户数据
        """
        filtered_data = user_data.copy()

        # 定义各角色可见字段
        role_permissions = {
            'self': [
                'id', 'username', 'real_name', 'email', 'phone',
                'gender', 'birthday', 'address', 'city', 'province',
                'postal_code', 'department', 'major', 'degree',
                'student_id', 'employee_id', 'join_date', 'avatar_url'
            ],
            'teacher': [
                'id', 'username', 'real_name', 'email', 'phone',
                'gender', 'department', 'major', 'degree', 'student_id'
            ],
            'admin': [
                'id', 'username', 'real_name', 'email', 'phone',
                'gender', 'birthday', 'address', 'city', 'province',
                'postal_code', 'department', 'major', 'degree',
                'student_id', 'employee_id', 'join_date', 'status',
                'created_at', 'updated_at', 'last_login', 'avatar_url'
            ],
            'stranger': [
                'id', 'username', 'real_name', 'department', 'major'
            ]
        }

        # 获取允许查看的字段
        allowed_fields = role_permissions.get(viewer_role, role_permissions['stranger'])

        # 只保留允许的字段
        filtered_data = {k: v for k, v in filtered_data.items() if k in allowed_fields}

        # 如果不包含敏感信息，进行脱敏处理
        if not include_sensitive and viewer_role != 'self':
            if 'email' in filtered_data:
                filtered_data['email'] = PrivacyFilter.mask_email(filtered_data['email'])
            if 'phone' in filtered_data:
                filtered_data['phone'] = PrivacyFilter.mask_phone_number(filtered_data['phone'])
            if 'address' in filtered_data:
                filtered_data['address'] = PrivacyFilter.mask_address(filtered_data['address'])
            if 'real_name' in filtered_data and viewer_role == 'stranger':
                filtered_data['real_name'] = PrivacyFilter.mask_name(filtered_data['real_name'])

        return filtered_data

class AuditLogger:
    """审计日志记录器"""

    @staticmethod
    def log_data_access(user_id: int, target_id: int, action: str,
                       ip_address: str, user_agent: str,
                       accessed_fields: list = None):
        """
        记录数据访问日志

        Args:
            user_id: 访问者ID
            target_id: 被访问目标ID
            action: 操作类型 (view/update/delete)
            ip_address: IP地址
            user_agent: 用户代理
            accessed_fields: 访问的字段列表
        """
        try:
            # 这里应该将日志保存到数据库或日志文件
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'target_id': target_id,
                'action': action,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'accessed_fields': accessed_fields or []
            }

            # 模拟保存日志
            logger.info(f"Audit Log: {log_entry}")

        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")

from datetime import datetime