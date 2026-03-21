"""
账户模型
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class Account(Base, TimestampMixin):
    """账户表"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="账户名称")
    type = Column(String(20), default="other", nullable=False, comment="账户类型")
    balance = Column(Numeric(15, 2), default=0.00, nullable=False, comment="当前余额")
    initial_balance = Column(Numeric(15, 2), default=0.00, nullable=False, comment="初始余额")
    icon = Column(String(10), nullable=True, comment="图标")
    color = Column(String(7), nullable=True, comment="颜色")
    is_default = Column(Boolean, default=False, nullable=False, comment="是否默认账户")
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    description = Column(Text, nullable=True, comment="账户描述")

    # 关系
    user = relationship("User", backref="accounts")

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', balance={self.balance})>"
