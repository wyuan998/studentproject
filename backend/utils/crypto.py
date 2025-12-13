# ========================================
# 学生信息管理系统 - 加密工具类
# ========================================

import base64
import hashlib
import hmac
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Union, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

from flask import current_app


class EncryptionManager:
    """加密管理器"""

    def __init__(self):
        """初始化加密管理器"""
        self._fernet = None
        self._init_encryption()

    def _init_encryption(self):
        """初始化加密器"""
        try:
            # 尝试从配置获取加密密钥
            encryption_key = current_app.config.get('ENCRYPTION_KEY')
            if encryption_key:
                self._fernet = Fernet(encryption_key.encode())
            else:
                # 生成新的密钥
                self._fernet = Fernet(self.generate_key())
        except Exception as e:
            current_app.logger.error(f"初始化加密器失败: {str(e)}")
            raise

    @staticmethod
    def generate_key() -> str:
        """
        生成加密密钥

        Returns:
            str: Base64编码的密钥
        """
        return Fernet.generate_key().decode()

    def encrypt(self, data: Union[str, bytes, Dict, Any]) -> str:
        """
        加密数据

        Args:
            data: 要加密的数据

        Returns:
            str: Base64编码的加密数据
        """
        try:
            if isinstance(data, (dict, list)):
                # 序列化JSON数据
                import json
                data_str = json.dumps(data, ensure_ascii=False)
                data_bytes = data_str.encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data

            encrypted_data = self._fernet.encrypt(data_bytes)
            return base64.b64encode(encrypted_data).decode('utf-8')

        except Exception as e:
            current_app.logger.error(f"数据加密失败: {str(e)}")
            raise ValueError(f"加密失败: {str(e)}")

    def decrypt(self, encrypted_data: str) -> Any:
        """
        解密数据

        Args:
            encrypted_data: Base64编码的加密数据

        Returns:
            Any: 解密后的数据
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')

            # 尝试反序列化JSON
            try:
                import json
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str

        except Exception as e:
            current_app.logger.error(f"数据解密失败: {str(e)}")
            raise ValueError(f"解密失败: {str(e)}")

    def encrypt_sensitive_field(self, field_value: str) -> str:
        """
        加密敏感字段

        Args:
            field_value: 字段值

        Returns:
            str: 加密后的值
        """
        return self.encrypt(field_value)

    def decrypt_sensitive_field(self, encrypted_value: str) -> str:
        """
        解密敏感字段

        Args:
            encrypted_value: 加密值

        Returns:
            str: 解密后的值
        """
        decrypted = self.decrypt(encrypted_value)
        return decrypted if isinstance(decrypted, str) else str(decrypted)


class HashManager:
    """哈希管理器"""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None, iterations: int = 100000) -> Tuple[str, str]:
        """
        哈希密码

        Args:
            password: 密码
            salt: 盐值（可选）
            iterations: 迭代次数

        Returns:
            Tuple[str, str]: (哈希值, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(32)

        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')

        # 使用PBKDF2进行密码哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )

        hashed = kdf.derive(password_bytes)
        hashed_hex = hashed.hex()

        return hashed_hex, salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str, iterations: int = 100000) -> bool:
        """
        验证密码

        Args:
            password: 密码
            hashed_password: 哈希密码
            salt: 盐值
            iterations: 迭代次数

        Returns:
            bool: 验证结果
        """
        try:
            new_hash, _ = HashManager.hash_password(password, salt, iterations)
            return hmac.compare_digest(new_hash, hashed_password)
        except Exception:
            return False

    @staticmethod
    def generate_hash(data: str, algorithm: str = 'sha256') -> str:
        """
        生成数据哈希

        Args:
            data: 数据
            algorithm: 哈希算法

        Returns:
            str: 哈希值
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        return hash_func(data.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
        """
        生成文件哈希

        Args:
            file_path: 文件路径
            algorithm: 哈希算法
            chunk_size: 块大小

        Returns:
            str: 哈希值
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    @staticmethod
    def generate_hmac(data: str, secret: str, algorithm: str = 'sha256') -> str:
        """
        生成HMAC

        Args:
            data: 数据
            secret: 密钥
            algorithm: 哈希算法

        Returns:
            str: HMAC值
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        hmac_obj = hmac.new(secret.encode('utf-8'), data.encode('utf-8'), hash_func)
        return hmac_obj.hexdigest()

    @staticmethod
    def verify_hmac(data: str, signature: str, secret: str, algorithm: str = 'sha256') -> bool:
        """
        验证HMAC

        Args:
            data: 数据
            signature: 签名
            secret: 密钥
            algorithm: 哈希算法

        Returns:
            bool: 验证结果
        """
        expected_signature = HashManager.generate_hmac(data, secret, algorithm)
        return hmac.compare_digest(expected_signature, signature)


class TokenManager:
    """令牌管理器"""

    def __init__(self):
        """初始化令牌管理器"""
        self.secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        self.algorithm = 'HS256'

    def generate_token(self, payload: Dict[str, Any], expiration_minutes: int = 60) -> str:
        """
        生成令牌

        Args:
            payload: 载荷数据
            expiration_minutes: 过期时间（分钟）

        Returns:
            str: JWT令牌
        """
        import jwt

        # 添加过期时间
        exp = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        payload.update({'exp': exp, 'iat': datetime.utcnow()})

        # 生成令牌
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        # 在某些版本的PyJWT中，token是bytes类型
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证令牌

        Args:
            token: JWT令牌

        Returns:
            Dict[str, Any]: 载荷数据

        Raises:
            ValueError: 令牌无效
        """
        import jwt

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError:
            raise ValueError("令牌无效")

    def refresh_token(self, token: str, expiration_minutes: int = 60) -> str:
        """
        刷新令牌

        Args:
            token: 原令牌
            expiration_minutes: 新令牌过期时间（分钟）

        Returns:
            str: 新令牌

        Raises:
            ValueError: 令牌无效
        """
        payload = self.verify_token(token)

        # 移除过期时间和其他时间相关字段
        payload.pop('exp', None)
        payload.pop('iat', None)

        return self.generate_token(payload, expiration_minutes)

    def generate_api_key(self, length: int = 32) -> str:
        """
        生成API密钥

        Args:
            length: 密钥长度

        Returns:
            str: API密钥
        """
        return secrets.token_urlsafe(length)

    def generate_webhook_signature(self, payload: str, secret: str = None) -> str:
        """
        生成Webhook签名

        Args:
            payload: 请求体
            secret: 签名密钥

        Returns:
            str: 签名
        """
        secret = secret or self.secret_key
        return HashManager.generate_hmac(payload, secret)


class AESEncryption:
    """AES加密类"""

    def __init__(self, key: Optional[str] = None):
        """
        初始化AES加密

        Args:
            key: 加密密钥（32字节）
        """
        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            self.key = os.urandom(32)

    def encrypt(self, plaintext: Union[str, bytes]) -> Dict[str, str]:
        """
        AES加密

        Args:
            plaintext: 明文

        Returns:
            Dict[str, str]: 加密数据（包含IV和密文）
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        # 生成随机IV
        iv = os.urandom(16)

        # 创建加密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # 添加PKCS7填充
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        # 加密
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return {
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
        }

    def decrypt(self, encrypted_data: Dict[str, str]) -> str:
        """
        AES解密

        Args:
            encrypted_data: 加密数据字典

        Returns:
            str: 明文
        """
        try:
            # 解码Base64
            iv = base64.b64decode(encrypted_data['iv'].encode('utf-8'))
            ciphertext = base64.b64decode(encrypted_data['ciphertext'].encode('utf-8'))

            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # 解密
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # 移除填充
            unpadder = PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

            return plaintext.decode('utf-8')

        except Exception as e:
            raise ValueError(f"AES解密失败: {str(e)}")


class SecureRandom:
    """安全随机数生成器"""

    @staticmethod
    def generate_token(length: int = 32, urlsafe: bool = True) -> str:
        """
        生成安全令牌

        Args:
            length: 令牌长度
            urlsafe: 是否URL安全

        Returns:
            str: 安全令牌
        """
        if urlsafe:
            return secrets.token_urlsafe(length)
        else:
            return secrets.token_hex(length // 2)

    @staticmethod
    def generate_uuid() -> str:
        """
        生成UUID

        Returns:
            str: UUID
        """
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def generate_password(
        length: int = 12,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_symbols: bool = True,
        exclude_ambiguous: bool = True
    ) -> str:
        """
        生成安全密码

        Args:
            length: 密码长度
            include_uppercase: 是否包含大写字母
            include_lowercase: 是否包含小写字母
            include_digits: 是否包含数字
            include_symbols: 是否包含特殊字符
            exclude_ambiguous: 是否排除易混淆字符

        Returns:
            str: 安全密码
        """
        chars = ''
        if include_lowercase:
            chars += string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_digits:
            chars += string.digits
        if include_symbols:
            chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'

        if exclude_ambiguous:
            ambiguous = '0O1lI'
            chars = ''.join(c for c in chars if c not in ambiguous)

        if not chars:
            raise ValueError("至少需要一种字符类型")

        # 确保密码包含所有要求的字符类型
        password = []
        if include_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if include_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if include_digits:
            password.append(secrets.choice(string.digits))
        if include_symbols:
            password.append(secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'))

        # 填充剩余长度
        remaining_length = length - len(password)
        if remaining_length > 0:
            password.extend(secrets.choice(chars) for _ in range(remaining_length))

        # 打乱顺序
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    @staticmethod
    def generate_session_id() -> str:
        """
        生成会话ID

        Returns:
            str: 会话ID
        """
        return secrets.token_urlsafe(32)


class DigitalSignature:
    """数字签名类"""

    def __init__(self, private_key: Optional[str] = None, public_key: Optional[str] = None):
        """
        初始化数字签名

        Args:
            private_key: 私钥
            public_key: 公钥
        """
        self.private_key = private_key
        self.public_key = public_key

        if not private_key or not public_key:
            self._generate_key_pair()

    def _generate_key_pair(self):
        """生成RSA密钥对"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        # 生成私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # 生成公钥
        self.public_key = self.private_key.public_key()

    def sign(self, data: str) -> str:
        """
        签名数据

        Args:
            data: 要签名的数据

        Returns:
            str: 签名
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        if isinstance(data, str):
            data = data.encode('utf-8')

        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def verify(self, data: str, signature: str) -> bool:
        """
        验证签名

        Args:
            data: 原始数据
            signature: 签名

        Returns:
            bool: 验证结果
        """
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding

            if isinstance(data, str):
                data = data.encode('utf-8')

            signature_bytes = base64.b64decode(signature.encode('utf-8'))

            self.public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except Exception:
            return False

    def get_public_key_pem(self) -> str:
        """
        获取PEM格式公钥

        Returns:
            str: PEM格式公钥
        """
        from cryptography.hazmat.primitives import serialization

        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return pem.decode('utf-8')


# 全局实例
_encryption_manager = None
_hash_manager = None
_token_manager = None


def get_encryption_manager() -> EncryptionManager:
    """获取加密管理器实例"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def get_hash_manager() -> HashManager:
    """获取哈希管理器实例"""
    global _hash_manager
    if _hash_manager is None:
        _hash_manager = HashManager()
    return _hash_manager


def get_token_manager() -> TokenManager:
    """获取令牌管理器实例"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


# 便捷函数
def encrypt_sensitive_data(data: Any) -> str:
    """加密敏感数据"""
    return get_encryption_manager().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> Any:
    """解密敏感数据"""
    return get_encryption_manager().decrypt(encrypted_data)


def hash_password(password: str) -> Tuple[str, str]:
    """哈希密码"""
    return get_hash_manager().hash_password(password)


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """验证密码"""
    return get_hash_manager().verify_password(password, hashed_password, salt)


def generate_secure_token(length: int = 32) -> str:
    """生成安全令牌"""
    return SecureRandom.generate_token(length)


def generate_jwt_token(payload: Dict[str, Any], expiration_minutes: int = 60) -> str:
    """生成JWT令牌"""
    return get_token_manager().generate_token(payload, expiration_minutes)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """验证JWT令牌"""
    return get_token_manager().verify_token(token)