# ========================================
# 学生信息管理系统 - 系统配置模型
# ========================================

import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Index, Boolean, JSON, Integer, Float
from sqlalchemy.orm import relationship
from extensions import db
from .base import BaseModel

class ConfigType(enum.Enum):
    """配置类型枚举"""
    SYSTEM = "system"           # 系统配置
    ACADEMIC = "academic"       # 学术配置
    NOTIFICATION = "notification"  # 通知配置
    SECURITY = "security"       # 安全配置
    EMAIL = "email"            # 邮件配置
    BACKUP = "backup"          # 备份配置
    UI = "ui"                 # 界面配置
    INTEGRATION = "integration"  # 集成配置
    FEATURE = "feature"        # 功能开关

class ConfigValueType(enum.Enum):
    """配置值类型枚举"""
    STRING = "string"         # 字符串
    INTEGER = "integer"       # 整数
    FLOAT = "float"          # 浮点数
    BOOLEAN = "boolean"      # 布尔值
    JSON = "json"            # JSON对象
    ARRAY = "array"          # 数组

class SystemConfig(BaseModel):
    """系统配置模型"""

    __tablename__ = 'system_configs'

    # 配置信息
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)  # 配置名称
    description = Column(Text)  # 配置描述
    category = Column(String(50))  # 配置分类

    # 类型信息
    config_type = Column(Enum(ConfigType), nullable=False)
    value_type = Column(Enum(ConfigValueType), nullable=False)

    # 配置值
    string_value = Column(String(1000))  # 字符串值
    integer_value = Column(Integer)      # 整数值
    float_value = Column(Float)          # 浮点数值
    boolean_value = Column(Boolean)      # 布尔值
    json_value = Column(JSON)            # JSON值

    # 约束信息
    min_value = Column(Float)            # 最小值
    max_value = Column(Float)            # 最大值
    allowed_values = Column(JSON)        # 允许的值列表
    validation_pattern = Column(String(200))  # 验证正则表达式

    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否启用
    is_required = Column(Boolean, default=False)  # 是否必填
    is_public = Column(Boolean, default=False)   # 是否公开（前端可访问）

    # 修改信息
    is_editable = Column(Boolean, default=True)  # 是否可编辑
    requires_restart = Column(Boolean, default=False)  # 是否需要重启生效
    last_modified_by = Column(db.CHAR(36), db.ForeignKey('users.id'))  # 最后修改人
    last_modified_at = Column(DateTime)  # 最后修改时间

    # 版本控制
    version = Column(String(20), default="1.0")  # 配置版本
    change_log = Column(Text)  # 变更日志

    # 缓存信息
    cache_ttl = Column(Integer, default=300)  # 缓存时间（秒）
    is_cached = Column(Boolean, default=True)  # 是否缓存

    # 排序
    sort_order = Column(Integer, default=0)  # 排序序号

    # 关系
    modifier = relationship("User", foreign_keys=[last_modified_by])

    # 索引
    __table_args__ = (
        Index('idx_type_category', 'config_type', 'category'),
        Index('idx_active_editable', 'is_active', 'is_editable'),
        Index('idx_sort_order', 'sort_order'),
    )

    def __init__(self, **kwargs):
        super(SystemConfig, self).__init__(**kwargs)

    @property
    def value(self):
        """获取配置值"""
        if self.value_type == ConfigValueType.STRING:
            return self.string_value
        elif self.value_type == ConfigValueType.INTEGER:
            return self.integer_value
        elif self.value_type == ConfigValueType.FLOAT:
            return self.float_value
        elif self.value_type == ConfigValueType.BOOLEAN:
            return self.boolean_value
        elif self.value_type == ConfigValueType.JSON:
            return self.json_value
        elif self.value_type == ConfigValueType.ARRAY:
            return self.json_value if isinstance(self.json_value, list) else []
        return None

    @value.setter
    def value(self, new_value):
        """设置配置值"""
        self.validate_value(new_value)

        if self.value_type == ConfigValueType.STRING:
            self.string_value = str(new_value) if new_value is not None else None
        elif self.value_type == ConfigValueType.INTEGER:
            self.integer_value = int(new_value) if new_value is not None else None
        elif self.value_type == ConfigValueType.FLOAT:
            self.float_value = float(new_value) if new_value is not None else None
        elif self.value_type == ConfigValueType.BOOLEAN:
            self.boolean_value = bool(new_value) if new_value is not None else None
        elif self.value_type == ConfigValueType.JSON:
            self.json_value = new_value
        elif self.value_type == ConfigValueType.ARRAY:
            self.json_value = new_value if isinstance(new_value, list) else [new_value]

        self.last_modified_at = datetime.utcnow()

    @property
    def display_value(self):
        """获取显示值"""
        value = self.value
        if value is None:
            return "未设置"

        if self.value_type == ConfigValueType.BOOLEAN:
            return "是" if value else "否"
        elif self.value_type == ConfigValueType.ARRAY:
            return ", ".join(str(v) for v in value) if value else ""
        elif self.value_type == ConfigValueType.JSON:
            return str(value) if value else "{}"
        else:
            return str(value)

    @property
    def display_type(self):
        """获取类型显示名称"""
        type_mapping = {
            ConfigValueType.STRING: "字符串",
            ConfigValueType.INTEGER: "整数",
            ConfigValueType.FLOAT: "浮点数",
            ConfigValueType.BOOLEAN: "布尔值",
            ConfigValueType.JSON: "JSON对象",
            ConfigValueType.ARRAY: "数组"
        }
        return type_mapping.get(self.value_type, "未知")

    def validate_value(self, value):
        """验证配置值"""
        if value is None:
            if self.is_required:
                raise ValueError(f"配置项 {self.key} 是必填项")
            return

        # 类型验证
        if self.value_type == ConfigValueType.STRING:
            if not isinstance(value, str):
                raise ValueError("值必须是字符串类型")
        elif self.value_type == ConfigValueType.INTEGER:
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError("值必须是整数类型")
        elif self.value_type == ConfigValueType.FLOAT:
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError("值必须是数字类型")
        elif self.value_type == ConfigValueType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError("值必须是布尔类型")
        elif self.value_type == ConfigValueType.JSON:
            if not isinstance(value, (dict, list)):
                raise ValueError("值必须是JSON对象或数组")

        # 范围验证
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"值不能小于 {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"值不能大于 {self.max_value}")

        # 允许值验证
        if self.allowed_values and value not in self.allowed_values:
            raise ValueError(f"值必须是以下之一: {', '.join(str(v) for v in self.allowed_values)}")

        # 正则表达式验证
        if self.validation_pattern and isinstance(value, str):
            import re
            if not re.match(self.validation_pattern, value):
                raise ValueError("值格式不正确")

    def update_value(self, new_value, user_id=None, change_description=None):
        """更新配置值"""
        old_value = self.value
        self.value = new_value

        if user_id:
            self.last_modified_by = user_id

        if change_description:
            self.add_change_log(change_description, old_value, new_value)

        self.save()

    def add_change_log(self, description, old_value=None, new_value=None):
        """添加变更日志"""
        timestamp = datetime.utcnow().isoformat()
        change_entry = {
            'timestamp': timestamp,
            'description': description,
            'old_value': old_value,
            'new_value': new_value
        }

        if self.change_log:
            try:
                import json
                change_history = json.loads(self.change_log)
            except:
                change_history = []
        else:
            change_history = []

        change_history.append(change_entry)
        import json
        self.change_log = json.dumps(change_history, ensure_ascii=False, indent=2)

    def get_change_history(self):
        """获取变更历史"""
        if not self.change_log:
            return []

        try:
            import json
            return json.loads(self.change_log)
        except:
            return []

    def enable(self):
        """启用配置"""
        self.is_active = True
        self.save()

    def disable(self):
        """禁用配置"""
        self.is_active = False
        self.save()

    def reset_to_default(self, default_value):
        """重置为默认值"""
        self.value = default_value
        self.add_change_log("重置为默认值", None, default_value)
        self.save()

    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(key=key, is_active=True).first()
        if config:
            return config.value
        return default

    @classmethod
    def set_config(cls, key, value, user_id=None, description=None):
        """设置配置值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.update_value(value, user_id, description)
        else:
            # 创建新配置
            config = cls(
                key=key,
                name=key,
                config_type=ConfigType.SYSTEM,
                value_type=ConfigValueType.STRING,
                value=value,
                last_modified_by=user_id
            )
            if description:
                config.add_change_log("创建配置", None, value)
            config.save()

        return config

    @classmethod
    def get_configs_by_type(cls, config_type, active_only=True):
        """根据类型获取配置"""
        query = cls.query.filter_by(config_type=config_type)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.sort_order, cls.key).all()

    @classmethod
    def get_public_configs(cls):
        """获取公开配置（前端可访问）"""
        return cls.query.filter_by(
            is_active=True,
            is_public=True
        ).order_by(cls.sort_order, cls.key).all()

    @classmethod
    def get_configs_dict(cls, config_type=None, active_only=True):
        """获取配置字典"""
        query = cls.query
        if config_type:
            query = query.filter_by(config_type=config_type)
        if active_only:
            query = query.filter_by(is_active=True)

        configs = query.order_by(cls.sort_order, cls.key).all()
        return {config.key: config.value for config in configs}

    @classmethod
    def batch_update(cls, updates, user_id=None):
        """批量更新配置"""
        updated_count = 0
        for key, value in updates.items():
            config = cls.query.filter_by(key=key).first()
            if config and config.is_editable:
                config.update_value(value, user_id, f"批量更新: {key}")
                updated_count += 1
        return updated_count

    @classmethod
    def export_configs(cls, config_type=None):
        """导出配置"""
        query = cls.query
        if config_type:
            query = query.filter_by(config_type=config_type)

        configs = query.all()
        export_data = []
        for config in configs:
            config_data = {
                'key': config.key,
                'name': config.name,
                'description': config.description,
                'config_type': config.config_type.value,
                'value_type': config.value_type.value,
                'value': config.value,
                'is_active': config.is_active,
                'category': config.category,
                'version': config.version
            }
            export_data.append(config_data)

        return export_data

    @classmethod
    def import_configs(cls, config_data, user_id=None, overwrite=False):
        """导入配置"""
        imported_count = 0
        for item in config_data:
            key = item.get('key')
            if not key:
                continue

            existing_config = cls.query.filter_by(key=key).first()

            if existing_config:
                if overwrite:
                    existing_config.value = item.get('value')
                    existing_config.name = item.get('name', existing_config.name)
                    existing_config.description = item.get('description', existing_config.description)
                    existing_config.last_modified_by = user_id
                    existing_config.add_change_log("导入配置更新")
                    existing_config.save()
                    imported_count += 1
            else:
                # 创建新配置
                new_config = cls(
                    key=key,
                    name=item.get('name', key),
                    description=item.get('description'),
                    config_type=ConfigType(item.get('config_type', 'system')),
                    value_type=ConfigValueType(item.get('value_type', 'string')),
                    value=item.get('value'),
                    is_active=item.get('is_active', True),
                    category=item.get('category'),
                    version=item.get('version', '1.0'),
                    last_modified_by=user_id
                )
                new_config.add_change_log("导入配置创建")
                new_config.save()
                imported_count += 1

        return imported_count

    def to_dict(self, include_value=True, include_change_log=False):
        """转换为字典"""
        data = super().to_dict()
        data['display_type'] = self.display_type
        data['display_value'] = self.display_value

        if include_value:
            data['value'] = self.value

        if include_change_log:
            data['change_history'] = self.get_change_history()

        # 移除敏感的内部字段
        data.pop('string_value', None)
        data.pop('integer_value', None)
        data.pop('float_value', None)
        data.pop('boolean_value', None)
        data.pop('json_value', None)

        return data

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', type='{self.config_type.value}', value='{self.display_value}')>"