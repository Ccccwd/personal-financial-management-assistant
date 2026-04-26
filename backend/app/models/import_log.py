"""
导入日志模型
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.config.database import Base, TimestampMixin
import enum


class ImportStatus(str, enum.Enum):
    """导入状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ImportLog(Base, TimestampMixin):
    """导入日志表"""
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    source = Column(String(50), nullable=False, default="wechat", comment="导入来源")
    file_name = Column(String(200), nullable=True, comment="文件名")
    file_size = Column(Integer, nullable=True, comment="文件大小(字节)")
    status = Column(String(20), nullable=False, default=ImportStatus.PENDING, comment="导入状态")
    total_records = Column(Integer, default=0, comment="总记录数")
    success_records = Column(Integer, default=0, comment="成功记录数")
    failed_records = Column(Integer, default=0, comment="失败记录数")
    skipped_records = Column(Integer, default=0, comment="跳过记录数(重复)")
    error_details = Column(JSON, nullable=True, comment="错误详情")
    import_summary = Column(Text, nullable=True, comment="导入摘要")

    def __repr__(self):
        return f"<ImportLog(id={self.id}, source='{self.source}', status='{self.status}')>"
