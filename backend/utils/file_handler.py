# ========================================
# 文件处理工具
# ========================================

import os
import uuid
import hashlib
from PIL import Image
from datetime import datetime
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """文件处理器，用于处理文件上传、压缩等操作"""

    def __init__(self, upload_folder: str = 'uploads', max_size: int = 5 * 1024 * 1024):
        """
        初始化文件处理器

        Args:
            upload_folder: 文件上传目录
            max_size: 最大文件大小（字节），默认5MB
        """
        self.upload_folder = upload_folder
        self.max_size = max_size
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

        # 确保上传目录存在
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

    def is_allowed_file(self, filename: str) -> bool:
        """检查文件是否为允许的图片类型"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def generate_filename(self, original_filename: str, user_id: int) -> str:
        """生成唯一的文件名"""
        ext = original_filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{user_id}_{timestamp}_{unique_id}.{ext}"

    def compress_image(self, image_path: str, quality: int = 85, max_width: int = 800, max_height: int = 800) -> Tuple[str, int]:
        """
        压缩图片

        Args:
            image_path: 图片路径
            quality: 压缩质量（1-100）
            max_width: 最大宽度
            max_height: 最大高度

        Returns:
            Tuple[压缩后的文件路径, 压缩后文件大小]
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式（处理PNG透明度问题）
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img

                # 计算新尺寸
                width, height = img.size
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 保存压缩后的图片
                compressed_path = image_path.replace('.', '_compressed.')
                img.save(compressed_path, 'JPEG', quality=quality, optimize=True)

                # 获取压缩后文件大小
                compressed_size = os.path.getsize(compressed_path)

                return compressed_path, compressed_size

        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            raise

    def save_avatar(self, file_data: bytes, filename: str, user_id: int) -> dict:
        """
        保存头像文件

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            user_id: 用户ID

        Returns:
            包含文件信息的字典
        """
        try:
            # 验证文件类型
            if not self.is_allowed_file(filename):
                raise ValueError(f"不支持的文件类型，支持的类型: {', '.join(self.allowed_extensions)}")

            # 验证文件大小
            if len(file_data) > self.max_size:
                raise ValueError(f"文件大小超过限制 ({self.max_size / 1024 / 1024:.1f}MB)")

            # 生成文件路径
            avatar_folder = os.path.join(self.upload_folder, 'avatars')
            if not os.path.exists(avatar_folder):
                os.makedirs(avatar_folder)

            filename = self.generate_filename(filename, user_id)
            file_path = os.path.join(avatar_folder, filename)

            # 保存原始文件
            with open(file_path, 'wb') as f:
                f.write(file_data)

            # 压缩图片
            compressed_path, compressed_size = self.compress_image(file_path)

            # 删除原始文件，保留压缩后的文件
            os.remove(file_path)
            os.rename(compressed_path, file_path)

            # 生成文件URL
            file_url = f"/api/files/avatars/{filename}"

            return {
                'filename': filename,
                'file_path': file_path,
                'file_url': file_url,
                'file_size': compressed_size,
                'original_size': len(file_data),
                'compression_ratio': (1 - compressed_size / len(file_data)) * 100
            }

        except Exception as e:
            logger.error(f"保存头像失败: {e}")
            # 清理临时文件
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise

    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def get_file_hash(self, file_data: bytes) -> str:
        """计算文件哈希值，用于检测重复文件"""
        return hashlib.md5(file_data).hexdigest()