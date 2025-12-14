# ========================================
# 学生信息管理系统 - 系统配置序列化模式
# ========================================

from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from extensions import ma
from models.system_config import SystemConfig, ConfigType, ConfigValueType

class SystemConfigSchema(SQLAlchemyAutoSchema):
    """系统配置序列化模式"""

    class Meta:
        model = SystemConfig
        load_instance = True
        include_fk = True

    # 添加虚拟字段
    display_value = fields.Method('get_display_value')
    display_type = fields.Method('get_display_type')
    config_type_name = fields.Method('get_config_type_name')
    value_type_name = fields.Method('get_value_type_name')

    def get_display_value(self, obj):
        """获取显示值"""
        return obj.display_value if obj else ""

    def get_display_type(self, obj):
        """获取类型显示名称"""
        return obj.display_type if obj else ""

    def get_config_type_name(self, obj):
        """获取配置类型名称"""
        if obj and obj.config_type:
            return obj.config_type.value
        return ""

    def get_value_type_name(self, obj):
        """获取值类型名称"""
        if obj and obj.value_type:
            return obj.value_type.value
        return ""

class SystemConfigCreateSchema(Schema):
    """系统配置创建模式"""

    # 基本信息
    key = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[a-zA-Z][a-zA-Z0-9_.-]*$', error="配置键格式不正确"),
        validate=validate.Length(min=1, max=100, error="配置键长度为1-100位")
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error="配置名称长度为1-200位")
    )
    description = fields.Str(
        validate=validate.Length(max=1000, error="描述长度不能超过1000位")
    )
    category = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50, error="配置分类长度为1-50位")
    )

    # 类型信息
    config_type = fields.Str(
        required=True,
        validate=validate.OneOf([t.value for t in ConfigType], error="无效的配置类型")
    )
    value_type = fields.Str(
        required=True,
        validate=validate.OneOf([t.value for t in ConfigValueType], error="无效的值类型")
    )

    # 配置值
    value = fields.Raw(required=True, description="配置值")

    # 约束信息
    min_value = fields.Float(validate=validate.Range(min=0, error="最小值不能为负数"))
    max_value = fields.Float(validate=validate.Range(min=0, error="最大值不能为负数"))
    allowed_values = fields.List(fields.Raw(), description="允许的值列表")
    validation_pattern = fields.Str(description="验证正则表达式")

    # 状态信息
    is_active = fields.Bool(missing=True, description="是否启用")
    is_required = fields.Bool(missing=False, description="是否必填")
    is_public = fields.Bool(missing=False, description="是否公开")

    # 修改信息
    is_editable = fields.Bool(missing=True, description="是否可编辑")
    requires_restart = fields.Bool(missing=False, description="是否需要重启生效")

    # 版本控制
    version = fields.Str(missing="1.0", description="配置版本")
    change_log = fields.Str(description="变更日志")

    # 缓存信息
    cache_ttl = fields.Int(missing=300, validate=validate.Range(min=0, max=3600, error="缓存时间为0-3600秒"))
    is_cached = fields.Bool(missing=True, description="是否缓存")

    # 排序
    sort_order = fields.Int(missing=0, validate=validate.Range(min=0, error="排序序号不能为负数"))

    @validates('key')
    def validate_key(self, value):
        """验证配置键唯一性"""
        if SystemConfig.query.filter_by(key=value).first():
            raise ValidationError("配置键已存在")

    @validates_schema
    def validate_constraints(self, data, **kwargs):
        """验证约束条件"""
        min_value = data.get('min_value')
        max_value = data.get('max_value')

        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValidationError("最小值不能大于最大值", field_name='min_value')

class SystemConfigUpdateSchema(Schema):
    """系统配置更新模式"""

    # 基本信息
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=1000))
    category = fields.Str(validate=validate.Length(min=1, max=50))

    # 配置值
    value = fields.Raw(description="配置值")

    # 约束信息
    min_value = fields.Float(validate=validate.Range(min=0))
    max_value = fields.Float(validate=validate.Range(min=0))
    allowed_values = fields.List(fields.Raw(), description="允许的值列表")
    validation_pattern = fields.Str(description="验证正则表达式")

    # 状态信息
    is_active = fields.Bool(description="是否启用")
    is_required = fields.Bool(description="是否必填")
    is_public = fields.Bool(description="是否公开")

    # 修改信息
    is_editable = fields.Bool(description="是否可编辑")
    requires_restart = fields.Bool(description="是否需要重启生效")

    # 版本控制
    version = fields.Str(validate=validate.Length(max=20), description="配置版本")
    change_log = fields.Str(description="变更日志")

    # 缓存信息
    cache_ttl = fields.Int(validate=validate.Range(min=0, max=3600))
    is_cached = fields.Bool(description="是否缓存")

    # 排序
    sort_order = fields.Int(validate=validate.Range(min=0))

class SystemConfigBatchUpdateSchema(Schema):
    """系统配置批量更新模式"""

    configs = fields.List(
        fields.Dict(keys=fields.Str(), values=fields.Raw()),
        required=True,
        validate=validate.Length(min=1, error="配置列表不能为空")
    )
    category = fields.Str(description="配置分类")

class SystemConfigSearchSchema(Schema):
    """系统配置搜索模式"""

    keyword = fields.Str(description="搜索关键词")
    config_type = fields.Str(
        validate=validate.OneOf([t.value for t in ConfigType]),
        description="配置类型筛选"
    )
    category = fields.Str(description="配置分类筛选")
    is_active = fields.Bool(description="是否启用筛选")
    is_public = fields.Bool(description="是否公开筛选")
    is_editable = fields.Bool(description="是否可编辑筛选")
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        missing="sort_order",
        validate=validate.OneOf(['key', 'name', 'category', 'config_type', 'sort_order', 'created_at', 'updated_at'])
    )
    sort_order = fields.Str(missing="asc", validate=validate.OneOf(['asc', 'desc']))

class SystemConfigImportSchema(Schema):
    """系统配置导入模式"""

    configs = fields.List(
        fields.Dict(),
        required=True,
        validate=validate.Length(min=1, error="配置列表不能为空")
    )
    overwrite = fields.Bool(missing=False, description="是否覆盖现有配置")
    validate_only = fields.Bool(missing=False, description="仅验证不导入")

class SystemConfigExportSchema(Schema):
    """系统配置导出模式"""

    category = fields.Str(description="配置分类")
    config_type = fields.Str(
        validate=validate.OneOf([t.value for t in ConfigType]),
        description="配置类型"
    )
    is_active = fields.Bool(description="是否启用")
    include_inactive = fields.Bool(missing=False, description="包含未激活配置")
    include_change_log = fields.Bool(missing=False, description="包含变更日志")
    format = fields.Str(
        missing="json",
        validate=validate.OneOf(['json', 'yaml', 'csv']),
        description="导出格式"
    )