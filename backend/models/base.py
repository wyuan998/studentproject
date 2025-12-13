# ========================================
# 学生信息管理系统 - 数据模型基类
# ========================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.mysql import CHAR
from extensions import db

class BaseModel(db.Model):
    """数据模型基类"""

    __abstract__ = True

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self):
        """保存到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """更新记录"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """删除记录"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def create(cls, **kwargs):
        """创建新记录"""
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """获取所有记录"""
        return cls.query.all()

    @classmethod
    def filter_by(cls, **kwargs):
        """过滤查询"""
        return cls.query.filter_by(**kwargs)

    @classmethod
    def filter(cls, *args):
        """复杂条件查询"""
        return cls.query.filter(*args)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"