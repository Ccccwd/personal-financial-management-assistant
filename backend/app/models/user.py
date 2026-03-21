"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.config.database import Base, TimestampMixin


class User(Base, TimestampMixin):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
