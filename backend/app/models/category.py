"""
分类模型
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """分类表"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    type = Column(String(20), default="expense", nullable=False, index=True, comment="分类类型")
    icon = Column(String(10), nullable=True, comment="图标")
    color = Column(String(7), nullable=True, comment="颜色")
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True, comment="父分类ID")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序序号")
    is_system = Column(Boolean, default=False, nullable=False, index=True, comment="是否系统分类")

    # 关系
    user = relationship("User", backref="categories")
    parent = relationship("Category", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"
