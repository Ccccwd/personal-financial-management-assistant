"""
交易记录模型
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """交易记录表"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    type = Column(String(20), default="expense", nullable=False, index=True, comment="交易类型")
    amount = Column(Numeric(15, 2), nullable=False, comment="金额")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True, comment="分类ID")
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True, comment="账户ID")
    to_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True, comment="转入账户ID")
    transaction_date = Column(DateTime, nullable=False, index=True, comment="交易时间")
    remark = Column(String(255), nullable=True, comment="备注")
    merchant_name = Column(String(100), nullable=True, comment="商户名称")
    product_name = Column(String(255), nullable=True, comment="商品名称")
    source = Column(String(20), default="manual", nullable=False, index=True, comment="来源")
    wechat_transaction_id = Column(String(64), unique=True, nullable=True, comment="微信交易流水号")
    tags = Column(JSON, nullable=True, comment="标签列表")
    location = Column(String(255), nullable=True, comment="地理位置")
    images = Column(JSON, nullable=True, comment="图片URL列表")
    ai_classified = Column(Boolean, default=False, nullable=False, comment="是否由AI分类")
    is_repeated = Column(Boolean, default=False, nullable=False, comment="是否标记为重复")

    # 关系
    user = relationship("User", backref="transactions")
    category = relationship("Category", backref="transactions")
    account = relationship("Account", foreign_keys=[account_id], backref="transactions")
    to_account = relationship("Account", foreign_keys=[to_account_id])

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.type}', amount={self.amount})>"
