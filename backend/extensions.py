# ========================================
# 学生信息管理系统 - Flask扩展初始化
# ========================================

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from sqlalchemy import MetaData

# 自定义元数据配置
# 设置约束命名约定
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# 初始化扩展实例
db = SQLAlchemy(metadata=metadata)
redis_client = FlaskRedis()