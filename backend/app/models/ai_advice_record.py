"""
AI 建议记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin


class AIAdviceRecord(Base, TimestampMixin):
    """AI 建议记录表"""
    __tablename__ = "ai_advice_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    advice_type = Column(String(20), default="financial", comment="建议类型")
    analysis_period_start = Column(DateTime, nullable=True, comment="分析周期开始")
    analysis_period_end = Column(DateTime, nullable=True, comment="分析周期结束")
    highlights = Column(JSON, nullable=True, comment="消费亮点")
    warnings = Column(JSON, nullable=True, comment="预警信息")
    suggestions = Column(JSON, nullable=True, comment="建议列表")
    budget_suggestion = Column(JSON, nullable=True, comment="预算建议")
    full_report = Column(Text, nullable=True, comment="完整报告")
    tokens_used = Column(Integer, default=0, comment="消耗Token数")
    from_cache = Column(Boolean, default=False, comment="是否来自缓存")

    # 关系
    user = relationship("User", backref="ai_advice_records")

    def __repr__(self):
        return f"<AIAdviceRecord(id={self.id}, user_id={self.user_id}, advice_type='{self.advice_type}')>"
