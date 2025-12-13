# ========================================
# 学生信息管理系统 - 响应工具类
# ========================================

from flask import jsonify, make_response
from datetime import datetime
from typing import Any, Dict, Optional, Union

class APIResponse:
    """API响应类"""

    @staticmethod
    def success(
        message: str = "操作成功",
        data: Any = None,
        status_code: int = 200,
        meta: Optional[Dict] = None
    ) -> tuple:
        """
        成功响应

        Args:
            message: 成功消息
            data: 响应数据
            status_code: HTTP状态码
            meta: 元数据信息

        Returns:
            tuple: (response_dict, status_code)
        """
        response_dict = {
            'success': True,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }

        if data is not None:
            response_dict['data'] = data

        if meta:
            response_dict['meta'] = meta

        return jsonify(response_dict), status_code

    @staticmethod
    def error(
        message: str = "操作失败",
        status_code: int = 400,
        error_code: Optional[str] = None,
        errors: Optional[Dict] = None,
        meta: Optional[Dict] = None
    ) -> tuple:
        """
        错误响应

        Args:
            message: 错误消息
            status_code: HTTP状态码
            error_code: 错误代码
            errors: 详细错误信息
            meta: 元数据信息

        Returns:
            tuple: (response_dict, status_code)
        """
        response_dict = {
            'success': False,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }

        if error_code:
            response_dict['error_code'] = error_code

        if errors:
            response_dict['errors'] = errors

        if meta:
            response_dict['meta'] = meta

        return jsonify(response_dict), status_code

    @staticmethod
    def validation_error(errors: Dict, message: str = "数据验证失败"):
        """数据验证错误响应"""
        return APIResponse.error(
            message=message,
            status_code=422,
            error_code='VALIDATION_ERROR',
            errors=errors
        )

    @staticmethod
    def not_found(message: str = "资源不存在", resource_type: str = None):
        """资源不存在响应"""
        if resource_type:
            message = f"{resource_type}不存在"
        return APIResponse.error(
            message=message,
            status_code=404,
            error_code='NOT_FOUND'
        )

    @staticmethod
    def unauthorized(message: str = "未授权访问"):
        """未授权响应"""
        return APIResponse.error(
            message=message,
            status_code=401,
            error_code='UNAUTHORIZED'
        )

    @staticmethod
    def forbidden(message: str = "权限不足"):
        """权限不足响应"""
        return APIResponse.error(
            message=message,
            status_code=403,
            error_code='FORBIDDEN'
        )

    @staticmethod
    def conflict(message: str = "资源冲突", error_code: str = 'CONFLICT'):
        """资源冲突响应"""
        return APIResponse.error(
            message=message,
            status_code=409,
            error_code=error_code
        )

    @staticmethod
    def too_many_requests(message: str = "请求过于频繁"):
        """请求频繁响应"""
        return APIResponse.error(
            message=message,
            status_code=429,
            error_code='TOO_MANY_REQUESTS'
        )

    @staticmethod
    def internal_error(message: str = "服务器内部错误"):
        """内部错误响应"""
        return APIResponse.error(
            message=message,
            status_code=500,
            error_code='INTERNAL_ERROR'
        )

    @staticmethod
    def paginated_response(
        items,
        total: int,
        page: int,
        per_page: int,
        message: str = "获取数据成功"
    ):
        """分页响应"""
        total_pages = (total + per_page - 1) // per_page

        meta = {
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages,
                'prev_num': page - 1 if page > 1 else None,
                'next_num': page + 1 if page < total_pages else None
            }
        }

        return APIResponse.success(
            message=message,
            data=items,
            meta=meta
        )

    @staticmethod
    def created_response(message: str = "创建成功", data: Any = None):
        """创建成功响应"""
        return APIResponse.success(
            message=message,
            data=data,
            status_code=201
        )

    @staticmethod
    def no_content_response():
        """无内容响应"""
        return '', 204

# 便捷函数
def success_response(message: str = "操作成功", data: Any = None, status_code: int = 200, meta: Dict = None) -> tuple:
    """成功响应便捷函数"""
    return APIResponse.success(message, data, status_code, meta)

def error_response(message: str = "操作失败", status_code: int = 400, error_code: str = None, errors: Dict = None) -> tuple:
    """错误响应便捷函数"""
    return APIResponse.error(message, status_code, error_code, errors)

def validation_error_response(errors: Dict, message: str = "数据验证失败") -> tuple:
    """验证错误响应便捷函数"""
    return APIResponse.validation_error(errors, message)

def not_found_response(message: str = "资源不存在", resource_type: str = None) -> tuple:
    """资源不存在响应便捷函数"""
    return APIResponse.not_found(message, resource_type)

def unauthorized_response(message: str = "未授权访问") -> tuple:
    """未授权响应便捷函数"""
    return APIResponse.unauthorized(message)

def forbidden_response(message: str = "权限不足") -> tuple:
    """权限不足响应便捷函数"""
    return APIResponse.forbidden(message)

def conflict_response(message: str = "资源冲突", error_code: str = 'CONFLICT') -> tuple:
    """资源冲突响应便捷函数"""
    return APIResponse.conflict(message, error_code)

def internal_error_response(message: str = "服务器内部错误") -> tuple:
    """内部错误响应便捷函数"""
    return APIResponse.internal_error(message)

def paginated_response(items, total: int, page: int, per_page: int, message: str = "获取数据成功") -> tuple:
    """分页响应便捷函数"""
    return APIResponse.paginated_response(items, total, page, per_page, message)

def created_response(message: str = "创建成功", data: Any = None) -> tuple:
    """创建成功响应便捷函数"""
    return APIResponse.created_response(message, data)

class ResponseBuilder:
    """响应构建器"""

    def __init__(self):
        self.message = ""
        self.data = None
        self.status_code = 200
        self.error_code = None
        self.errors = None
        self.meta = None
        self.success = True

    def with_message(self, message: str):
        """设置消息"""
        self.message = message
        return self

    def with_data(self, data: Any):
        """设置数据"""
        self.data = data
        return self

    def with_status_code(self, status_code: int):
        """设置状态码"""
        self.status_code = status_code
        self.success = 200 <= status_code < 300
        return self

    def with_error_code(self, error_code: str):
        """设置错误代码"""
        self.error_code = error_code
        self.success = False
        return self

    def with_errors(self, errors: Dict):
        """设置详细错误"""
        self.errors = errors
        self.success = False
        return self

    def with_meta(self, meta: Dict):
        """设置元数据"""
        self.meta = meta
        return self

    def build(self) -> tuple:
        """构建响应"""
        if self.success:
            return APIResponse.success(self.message, self.data, self.status_code, self.meta)
        else:
            return APIResponse.error(self.message, self.status_code, self.error_code, self.errors, self.meta)

def make_file_response(file_data, filename, content_type='application/octet-stream'):
    """创建文件响应"""
    response = make_response(file_data)
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = content_type
    return response

def make_csv_response(csv_data, filename):
    """创建CSV响应"""
    return make_file_response(csv_data, filename, 'text/csv')

def make_excel_response(excel_data, filename):
    """创建Excel响应"""
    return make_file_response(excel_data, filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def make_pdf_response(pdf_data, filename):
    """创建PDF响应"""
    return make_file_response(pdf_data, filename, 'application/pdf')