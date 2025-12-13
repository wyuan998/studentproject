# ========================================
# 学生信息管理系统 - 认证工具类
# ========================================

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, g
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    decode_token, get_jti, get_jwt_identity
)

from ..models import User, db


class AuthManager:
    """认证管理器"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        密码哈希

        Args:
            password: 明文密码

        Returns:
            str: 哈希后的密码
        """
        return generate_password_hash(password, method='pbkdf2:sha256')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            hashed_password: 哈希密码

        Returns:
            bool: 验证结果
        """
        return check_password_hash(hashed_password, password)

    @staticmethod
    def generate_tokens(user_id: int, additional_claims: Optional[Dict] = None) -> Dict[str, Any]:
        """
        生成访问令牌和刷新令牌

        Args:
            user_id: 用户ID
            additional_claims: 额外的声明信息

        Returns:
            Dict[str, Any]: 包含访问令牌、刷新令牌和过期时间
        """
        now = datetime.utcnow()

        # 基础声明
        claims = {
            'user_id': user_id,
            'iat': now,
            'type': 'access'
        }

        # 添加额外声明
        if additional_claims:
            claims.update(additional_claims)

        # 生成访问令牌
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
            expires_delta=timedelta(
                seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            )
        )

        # 生成刷新令牌
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(
                seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
            )
        )

        # 解码令牌获取JTI和过期时间
        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_jti': access_decoded['jti'],
            'refresh_jti': refresh_decoded['jti'],
            'access_expires_at': datetime.fromtimestamp(access_decoded['exp']),
            'refresh_expires_at': datetime.fromtimestamp(refresh_decoded['exp'])
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            Dict[str, Any]: 新的访问令牌信息

        Raises:
            Exception: 刷新令牌无效或过期
        """
        try:
            decoded = decode_token(refresh_token)
            user_id = decoded['sub']

            # 获取用户信息
            user = User.query.get(user_id)
            if not user or not user.is_active():
                raise Exception('用户不存在或已被禁用')

            # 生成新的访问令牌
            access_token = create_access_token(
                identity=user_id,
                additional_claims={
                    'role': user.role.value,
                    'permissions': user.get_permissions()
                }
            )

            access_decoded = decode_token(access_token)

            return {
                'access_token': access_token,
                'access_jti': access_decoded['jti'],
                'access_expires_at': datetime.fromtimestamp(access_decoded['exp'])
            }

        except Exception as e:
            raise Exception(f'刷新令牌无效: {str(e)}')

    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """
        验证令牌

        Args:
            token: JWT令牌

        Returns:
            Dict[str, Any]: 令牌信息

        Raises:
            Exception: 令牌无效
        """
        try:
            decoded = decode_token(token)

            # 检查用户是否存在且激活
            user_id = decoded['sub']
            user = User.query.get(user_id)

            if not user or not user.is_active():
                raise Exception('用户不存在或已被禁用')

            return {
                'user_id': user_id,
                'jti': decoded['jti'],
                'exp': decoded['exp'],
                'iat': decoded['iat'],
                'type': decoded.get('type', 'unknown')
            }

        except jwt.ExpiredSignatureError:
            raise Exception('令牌已过期')
        except jwt.InvalidTokenError:
            raise Exception('令牌无效')

    @staticmethod
    def revoke_token(jti: str) -> bool:
        """
        撤销令牌

        Args:
            jti: 令牌JTI

        Returns:
            bool: 是否成功撤销
        """
        try:
            # 这里可以将JTI添加到黑名单中
            # 例如使用Redis存储黑名单
            from extensions import cache
            cache.set(f"revoked_token:{jti}", "true", timeout=86400)  # 24小时
            return True
        except Exception:
            return False

    @staticmethod
    def is_token_revoked(jti: str) -> bool:
        """
        检查令牌是否被撤销

        Args:
            jti: 令牌JTI

        Returns:
            bool: 是否被撤销
        """
        try:
            from extensions import cache
            return cache.get(f"revoked_token:{jti}") is not None
        except Exception:
            return False


class PasswordManager:
    """密码管理器"""

    @staticmethod
    def generate_password(length: int = 12, include_symbols: bool = True) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度
            include_symbols: 是否包含特殊字符

        Returns:
            str: 生成的密码
        """
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        if include_symbols:
            alphabet += '!@#$%^&*()_+-=[]{}|;:,.<>?'

        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            'valid': True,
            'score': 0,
            'issues': [],
            'suggestions': []
        }

        # 长度检查
        if len(password) < 8:
            result['valid'] = False
            result['issues'].append('密码长度至少8位')
            result['suggestions'].append('增加密码长度')
        else:
            result['score'] += 1

        # 包含小写字母
        if not any(c.islower() for c in password):
            result['issues'].append('密码应包含小写字母')
            result['suggestions'].append('添加小写字母')
        else:
            result['score'] += 1

        # 包含大写字母
        if not any(c.isupper() for c in password):
            result['issues'].append('密码应包含大写字母')
            result['suggestions'].append('添加大写字母')
        else:
            result['score'] += 1

        # 包含数字
        if not any(c.isdigit() for c in password):
            result['issues'].append('密码应包含数字')
            result['suggestions'].append('添加数字')
        else:
            result['score'] += 1

        # 包含特殊字符
        if not any(not c.isalnum() for c in password):
            result['issues'].append('密码应包含特殊字符')
            result['suggestions'].append('添加特殊字符')
        else:
            result['score'] += 1

        # 常见密码检查
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'root', 'user', 'test'
        ]
        if password.lower() in common_passwords:
            result['valid'] = False
            result['issues'].append('密码过于常见')
            result['suggestions'].append('使用更独特的密码')

        # 评分等级
        if result['score'] <= 2:
            result['strength'] = 'weak'
        elif result['score'] <= 3:
            result['strength'] = 'medium'
        elif result['score'] <= 4:
            result['strength'] = 'strong'
        else:
            result['strength'] = 'very_strong'

        return result


class SessionManager:
    """会话管理器"""

    @staticmethod
    def create_session(user_id: int, device_info: Optional[Dict] = None) -> str:
        """
        创建用户会话

        Args:
            user_id: 用户ID
            device_info: 设备信息

        Returns:
            str: 会话ID
        """
        import uuid

        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'device_info': device_info or {},
            'ip_address': request.environ.get('REMOTE_ADDR', '')
        }

        # 存储会话到Redis
        from extensions import cache
        cache.set(f"session:{session_id}", session_data, timeout=86400)  # 24小时

        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 会话信息
        """
        try:
            from extensions import cache
            return cache.get(f"session:{session_id}")
        except Exception:
            return None

    @staticmethod
    def update_session_activity(session_id: str) -> bool:
        """
        更新会话活动时间

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功更新
        """
        try:
            from extensions import cache
            session_data = cache.get(f"session:{session_id}")
            if session_data:
                session_data['last_activity'] = datetime.utcnow().isoformat()
                cache.set(f"session:{session_id}", session_data, timeout=86400)
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def destroy_session(session_id: str) -> bool:
        """
        销毁会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功销毁
        """
        try:
            from extensions import cache
            cache.delete(f"session:{session_id}")
            return True
        except Exception:
            return False

    @staticmethod
    def get_user_sessions(user_id: int) -> list:
        """
        获取用户的所有会话

        Args:
            user_id: 用户ID

        Returns:
            list: 会话列表
        """
        # 这里需要实现更复杂的逻辑来搜索特定用户的所有会话
        # 可能需要使用Redis的SCAN功能或维护用户会话索引
        return []


class SecurityManager:
    """安全管理器"""

    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        生成API密钥

        Args:
            length: 密钥长度

        Returns:
            str: API密钥
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_csrf_token() -> str:
        """
        生成CSRF令牌

        Returns:
            str: CSRF令牌
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """
        验证Webhook签名

        Args:
            payload: 请求体
            signature: 签名
            secret: 密钥

        Returns:
            bool: 验证结果
        """
        expected_signature = hashlib.hmac_sha256(
            secret.encode(),
            payload.encode()
        ).hexdigest()

        return secrets.compare_digest(expected_signature, signature)

    @staticmethod
    def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
        """
        加密敏感数据

        Args:
            data: 要加密的数据
            key: 加密密钥（可选）

        Returns:
            str: 加密后的数据
        """
        from cryptography.fernet import Fernet

        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY')

        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()

    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
        """
        解密敏感数据

        Args:
            encrypted_data: 加密的数据
            key: 解密密钥（可选）

        Returns:
            str: 解密后的数据
        """
        from cryptography.fernet import Fernet

        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY')

        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()


class TwoFactorAuth:
    """双因素认证"""

    @staticmethod
    def generate_secret() -> str:
        """
        生成2FA密钥

        Returns:
            str: 密钥
        """
        import pyotp
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(user_email: str, secret: str) -> str:
        """
        生成2FA二维码

        Args:
            user_email: 用户邮箱
            secret: 2FA密钥

        Returns:
            str: 二维码URL
        """
        import pyotp
        import qrcode
        from io import BytesIO
        import base64

        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            user_email,
            issuer_name="学生信息管理系统"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def verify_code(secret: str, token: str) -> bool:
        """
        验证2FA代码

        Args:
            secret: 2FA密钥
            token: 用户输入的代码

        Returns:
            bool: 验证结果
        """
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # 允许1个时间窗口的偏差


# 便捷函数
def get_current_user() -> Optional[User]:
    """获取当前登录用户"""
    try:
        if hasattr(g, 'current_user') and g.current_user:
            return g.current_user

        user_id = get_jwt_identity()
        if user_id:
            g.current_user = User.query.get(user_id)
            return g.current_user

    except Exception:
        pass

    return None


def require_auth(f):
    """认证装饰器（简化版）"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            from ..utils.responses import unauthorized_response
            return unauthorized_response("需要登录")

        return f(*args, **kwargs)

    return decorated_function