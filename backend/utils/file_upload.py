# ========================================
# 学生信息管理系统 - 文件上传工具类
# ========================================

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, BinaryIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
import magic
from flask import current_app, request

from ..utils.rate_limit import check_rate_limit


class FileUploadHandler:
    """文件上传处理器"""

    def __init__(self):
        self.upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {})
        self.max_file_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
        self.max_image_size = current_app.config.get('MAX_IMAGE_SIZE', (1920, 1080))

        # 确保上传目录存在
        self._ensure_upload_directories()

    def _ensure_upload_directories(self):
        """确保上传目录存在"""
        directories = [
            self.upload_folder,
            os.path.join(self.upload_folder, 'images'),
            os.path.join(self.upload_folder, 'documents'),
            os.path.join(self.upload_folder, 'exports'),
            os.path.join(self.upload_folder, 'temp'),
            os.path.join(self.upload_folder, 'avatars')
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def upload_file(
        self,
        file: FileStorage,
        folder: str = 'general',
        allowed_extensions: List[str] = None,
        max_size: int = None,
        generate_thumbnail: bool = False,
        custom_filename: str = None
    ) -> Dict[str, Any]:
        """
        上传文件

        Args:
            file: 文件对象
            folder: 存储文件夹
            allowed_extensions: 允许的文件扩展名
            max_size: 最大文件大小（字节）
            generate_thumbnail: 是否生成缩略图
            custom_filename: 自定义文件名

        Returns:
            Dict[str, Any]: 上传结果
        """
        try:
            # 检查限流
            if not check_rate_limit('upload', '10/minute'):
                return {
                    'success': False,
                    'error': '上传频率超限',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }

            # 验证文件
            validation_result = self._validate_file(file, allowed_extensions, max_size)
            if not validation_result['valid']:
                return validation_result

            # 生成文件名
            if custom_filename:
                filename = secure_filename(custom_filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            else:
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}{ext}"

            # 确定存储路径
            target_folder = os.path.join(self.upload_folder, folder)
            Path(target_folder).mkdir(parents=True, exist_ok=True)
            file_path = os.path.join(target_folder, unique_filename)

            # 保存文件
            file.save(file_path)

            # 获取文件信息
            file_info = self._get_file_info(file_path)
            file_hash = self._calculate_file_hash(file_path)

            # 如果是图片，进行额外处理
            thumbnail_path = None
            if self._is_image_file(file_path) and generate_thumbnail:
                thumbnail_path = self._generate_thumbnail(file_path)

            # 构建结果
            result = {
                'success': True,
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_path': file_path,
                'file_size': file_info['size'],
                'mime_type': file_info['mime_type'],
                'file_hash': file_hash,
                'upload_time': datetime.utcnow().isoformat(),
                'folder': folder
            }

            if thumbnail_path:
                result['thumbnail_path'] = thumbnail_path

            return result

        except Exception as e:
            current_app.logger.error(f"文件上传失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UPLOAD_FAILED'
            }

    def upload_multiple_files(
        self,
        files: List[FileStorage],
        folder: str = 'general',
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量上传文件

        Args:
            files: 文件列表
            folder: 存储文件夹
            **kwargs: 其他upload_file参数

        Returns:
            Dict[str, Any]: 上传结果
        """
        results = {
            'success': True,
            'uploaded_files': [],
            'failed_files': [],
            'total_count': len(files),
            'success_count': 0,
            'failed_count': 0
        }

        for file in files:
            if file and file.filename:
                result = self.upload_file(file, folder, **kwargs)
                if result['success']:
                    results['uploaded_files'].append(result)
                    results['success_count'] += 1
                else:
                    results['failed_files'].append({
                        'filename': file.filename,
                        'error': result['error']
                    })
                    results['failed_count'] += 1

        if results['failed_count'] > 0:
            results['success'] = False

        return results

    def delete_file(self, file_path: str, delete_thumbnail: bool = True) -> Dict[str, Any]:
        """
        删除文件

        Args:
            file_path: 文件路径
            delete_thumbnail: 是否同时删除缩略图

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            file_path = Path(file_path)
            thumbnail_path = None

            # 查找缩略图
            if delete_thumbnail and file_path.exists():
                thumbnail_dir = file_path.parent / 'thumbnails'
                if thumbnail_dir.exists():
                    potential_thumbnail = thumbnail_dir / f"{file_path.stem}_thumb{file_path.suffix}"
                    if potential_thumbnail.exists():
                        thumbnail_path = potential_thumbnail

            # 删除文件
            if file_path.exists():
                file_path.unlink()

                # 删除空目录
                try:
                    if not list(file_path.parent.iterdir()):
                        file_path.parent.rmdir()
                except OSError:
                    pass  # 目录不为空

            # 删除缩略图
            if thumbnail_path and thumbnail_path.exists():
                thumbnail_path.unlink()

            return {
                'success': True,
                'message': '文件删除成功'
            }

        except Exception as e:
            current_app.logger.error(f"文件删除失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DELETE_FAILED'
            }

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {'error': '文件不存在'}

            stat = file_path.stat()
            mime_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'

            # 如果是图片，获取额外信息
            extra_info = {}
            if self._is_image_file(file_path):
                try:
                    with Image.open(file_path) as img:
                        extra_info.update({
                            'width': img.width,
                            'height': img.height,
                            'format': img.format,
                            'mode': img.mode
                        })
                except Exception:
                    pass

            return {
                'filename': file_path.name,
                'file_path': str(file_path),
                'size': stat.st_size,
                'mime_type': mime_type,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                **extra_info
            }

        except Exception as e:
            return {'error': str(e)}

    def _validate_file(
        self,
        file: FileStorage,
        allowed_extensions: List[str] = None,
        max_size: int = None
    ) -> Dict[str, Any]:
        """验证文件"""
        # 检查文件是否存在
        if not file or not file.filename:
            return {
                'success': False,
                'error': '未选择文件',
                'error_code': 'NO_FILE'
            }

        # 检查文件大小
        file_size = len(file.read())
        file.seek(0)  # 重置文件指针

        max_size = max_size or self.max_file_size
        if file_size > max_size:
            return {
                'success': False,
                'error': f'文件大小超过限制 ({max_size / 1024 / 1024:.1f}MB)',
                'error_code': 'FILE_TOO_LARGE'
            }

        # 检查文件扩展名
        filename = secure_filename(file.filename)
        if not filename:
            return {
                'success': False,
                'error': '文件名无效',
                'error_code': 'INVALID_FILENAME'
            }

        _, ext = os.path.splitext(filename.lower())
        allowed_extensions = allowed_extensions or self.allowed_extensions.get('*', [])

        if allowed_extensions and ext not in allowed_extensions:
            return {
                'success': False,
                'error': f'不支持的文件类型: {ext}',
                'error_code': 'UNSUPPORTED_FILE_TYPE'
            }

        # 检查MIME类型
        mime_type = mimetypes.guess_type(filename)[0]
        if mime_type and mime_type.startswith('image/') and not self._validate_image_content(file):
            return {
                'success': False,
                'error': '图片文件内容无效',
                'error_code': 'INVALID_IMAGE_CONTENT'
            }

        return {'success': True, 'valid': True}

    def _validate_image_content(self, file: FileStorage) -> bool:
        """验证图片内容"""
        try:
            file.seek(0)
            image = Image.open(file)
            image.verify()
            file.seek(0)
            return True
        except Exception:
            return False

    def _is_image_file(self, file_path: str) -> bool:
        """判断是否为图片文件"""
        mime_type = mimetypes.guess_type(file_path)[0]
        return mime_type and mime_type.startswith('image/')

    def _generate_thumbnail(self, image_path: str, size: Tuple[int, int] = (300, 300)) -> str:
        """生成缩略图"""
        try:
            image_path = Path(image_path)
            thumbnail_dir = image_path.parent / 'thumbnails'
            thumbnail_dir.mkdir(exist_ok=True)

            thumbnail_name = f"{image_path.stem}_thumb{image_path.suffix}"
            thumbnail_path = thumbnail_dir / thumbnail_name

            with Image.open(image_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # 生成缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, optimize=True, quality=85)

            return str(thumbnail_path)

        except Exception as e:
            current_app.logger.error(f"生成缩略图失败: {str(e)}")
            return None

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件基本信息"""
        file_path = Path(file_path)
        stat = file_path.stat()
        mime_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'

        return {
            'size': stat.st_size,
            'mime_type': mime_type
        }


class FileOrganizer:
    """文件组织器"""

    def __init__(self):
        self.base_path = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.folder_rules = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
            'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
            'archive': ['zip', 'rar', '7z', 'tar', 'gz']
        }

    def organize_file(self, file_path: str) -> str:
        """
        根据文件类型组织文件

        Args:
            file_path: 文件路径

        Returns:
            str: 新的文件路径
        """
        file_path = Path(file_path)

        # 确定文件类型
        file_type = self._determine_file_type(file_path)

        # 创建目标目录
        target_dir = Path(self.base_path) / file_type
        target_dir.mkdir(parents=True, exist_ok=True)

        # 移动文件
        target_path = target_dir / file_path.name
        counter = 1

        # 如果文件已存在，添加序号
        while target_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            target_path = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        file_path.rename(target_path)
        return str(target_path)

    def _determine_file_type(self, file_path: Path) -> str:
        """确定文件类型"""
        ext = file_path.suffix.lower().lstrip('.')

        for file_type, extensions in self.folder_rules.items():
            if ext in extensions:
                return file_type

        return 'other'

    def cleanup_empty_folders(self) -> int:
        """清理空文件夹"""
        cleaned_count = 0
        base_path = Path(self.base_path)

        for root, dirs, files in os.walk(base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not list(dir_path.iterdir()):
                        dir_path.rmdir()
                        cleaned_count += 1
                except OSError:
                    pass

        return cleaned_count


class FileValidator:
    """文件验证器"""

    @staticmethod
    def scan_for_malware(file_path: str) -> Dict[str, Any]:
        """
        扫描文件恶意内容

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 扫描结果
        """
        try:
            # 基础检查
            file_path = Path(file_path)

            # 检查文件大小异常
            if file_path.stat().st_size == 0:
                return {'safe': False, 'reason': '空文件'}

            # 检查文件扩展名与实际内容是否匹配
            mime_type = magic.from_file(str(file_path), mime=True)
            file_ext = file_path.suffix.lower()

            # 可疑的扩展名检查
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            if file_ext in suspicious_extensions:
                return {'safe': False, 'reason': '可疑文件扩展名'}

            # 检查文件头
            with open(file_path, 'rb') as f:
                header = f.read(1024)

                # 检查是否包含可疑内容
                suspicious_patterns = [
                    b'eval(',
                    b'exec(',
                    b'system(',
                    b'shell_exec',
                    b'<script',
                    b'javascript:'
                ]

                for pattern in suspicious_patterns:
                    if pattern in header.lower():
                        return {'safe': False, 'reason': '包含可疑代码'}

            return {'safe': True, 'mime_type': mime_type}

        except Exception as e:
            return {'safe': False, 'reason': f'扫描失败: {str(e)}'}

    @staticmethod
    def validate_file_content(file_path: str, expected_type: str = None) -> Dict[str, Any]:
        """
        验证文件内容

        Args:
            file_path: 文件路径
            expected_type: 期望的文件类型

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            file_path = Path(file_path)

            # 使用python-magic获取真实MIME类型
            real_mime = magic.from_file(str(file_path), mime=True)

            # 从文件扩展名推断MIME类型
            expected_mime = mimetypes.guess_type(str(file_path))[0]

            validation_result = {
                'real_mime': real_mime,
                'expected_mime': expected_mime,
                'valid': True
            }

            # 检查MIME类型是否匹配
            if expected_mime and expected_mime != real_mime:
                # 允许一些常见的MIME类型差异
                allowed_differences = {
                    'text/plain': ['application/octet-stream'],
                    'application/octet-stream': ['text/plain']
                }

                if real_mime not in allowed_differences.get(expected_mime, []):
                    validation_result['valid'] = False
                    validation_result['reason'] = f'MIME类型不匹配: {expected_mime} vs {real_mime}'

            return validation_result

        except Exception as e:
            return {
                'valid': False,
                'reason': f'验证失败: {str(e)}'
            }


# 便捷函数
def upload_profile_picture(file: FileStorage, user_id: int) -> Dict[str, Any]:
    """上传用户头像"""
    handler = FileUploadHandler()

    result = handler.upload_file(
        file=file,
        folder='avatars',
        allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        max_size=5 * 1024 * 1024,  # 5MB
        generate_thumbnail=True,
        custom_filename=f"user_{user_id}_avatar"
    )

    if result['success']:
        # 更新用户头像路径（这里需要根据实际业务逻辑处理）
        pass

    return result


def upload_document(file: FileStorage, document_type: str = 'general') -> Dict[str, Any]:
    """上传文档文件"""
    handler = FileUploadHandler()

    allowed_extensions = {
        'general': ['.pdf', '.doc', '.docx', '.txt'],
        'spreadsheet': ['.xls', '.xlsx', '.csv'],
        'presentation': ['.ppt', '.pptx'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    }

    return handler.upload_file(
        file=file,
        folder=f'documents/{document_type}',
        allowed_extensions=allowed_extensions.get(document_type, []),
        max_size=20 * 1024 * 1024  # 20MB
    )


def create_export_file(data: Any, filename: str, format_type: str = 'csv') -> Dict[str, Any]:
    """创建导出文件"""
    try:
        handler = FileUploadHandler()
        export_folder = os.path.join(handler.upload_folder, 'exports')
        Path(export_folder).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"{filename}_{timestamp}.{format_type}"
        file_path = os.path.join(export_folder, export_filename)

        if format_type == 'csv':
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                if isinstance(data, list) and data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)

        elif format_type == 'json':
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        return {
            'success': True,
            'file_path': file_path,
            'filename': export_filename,
            'download_url': f'/api/v1/files/download/{export_filename}'
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_code': 'EXPORT_FAILED'
        }