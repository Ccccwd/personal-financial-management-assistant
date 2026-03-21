"""
预算模型
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class Budget(Base, TimestampMixin):
    """预算表"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True, comment="分类ID")
    amount = Column(Numeric(15, 2), nullable=False, comment="预算金额")
    period_type = Column(String(20), default="monthly", nullable=False, comment="周期类型")
    year = Column(Integer, nullable=False, comment="年份")
    month = Column(Integer, nullable=True, comment="月份")
    alert_threshold = Column(Integer, default=80, nullable=False, comment="预警阈值")
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")

    # 关系
    user = relationship("User", backref="budgets")
    category = relationship("Category", backref="budgets")

    def __repr__(self):
        return f"<Budget(id={self.id}, amount={self.amount}, period='{self.period_type}')>"
