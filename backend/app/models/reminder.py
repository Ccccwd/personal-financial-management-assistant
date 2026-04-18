"""
提醒模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Time, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class Reminder(Base, TimestampMixin):
    """提醒表"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    type = Column(String(20), nullable=False, index=True, comment="提醒类型: daily/budget/recurring/report")
    title = Column(String(100), nullable=False, comment="提醒标题")
    content = Column(String(500), nullable=True, comment="提醒内容")
    remind_time = Column(Time, nullable=True, comment="提醒时间")
    remind_day = Column(Integer, nullable=True, comment="提醒日期(1-31)")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True, comment="分类ID")
    amount = Column(Numeric(15, 2), nullable=True, comment="金额阈值")
    is_enabled = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")
    last_reminded_at = Column(DateTime, nullable=True, comment="上次提醒时间")

    # 关系
    user = relationship("User", backref="reminders")
    category = relationship("Category", backref="reminders")

    def __repr__(self):
        return f"<Reminder(id={self.id}, type='{self.type}', title='{self.title}')>"
