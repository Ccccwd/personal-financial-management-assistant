"""
余额历史模型
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class BalanceHistory(Base, TimestampMixin):
    """余额历史表"""
    __tablename__ = "balance_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True, comment="账户ID")
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True, comment="交易ID")
    change_type = Column(String(20), nullable=False, comment="变化类型: income/expense/transfer/adjust")
    amount_before = Column(Numeric(15, 2), nullable=False, comment="变化前余额")
    amount_after = Column(Numeric(15, 2), nullable=False, comment="变化后余额")
    change_amount = Column(Numeric(15, 2), nullable=False, comment="变化金额")
    description = Column(String(255), nullable=True, comment="描述")

    # 关系
    account = relationship("Account", backref="balance_histories")

    def __repr__(self):
        return f"<BalanceHistory(id={self.id}, account_id={self.account_id}, change_type='{self.change_type}')>"
