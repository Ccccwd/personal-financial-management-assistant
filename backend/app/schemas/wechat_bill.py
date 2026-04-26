"""
微信账单导入 Schema
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ImportPreviewItem(BaseModel):
    """单条预览数据"""
    transaction_time: str
    transaction_type: str
    counterparty: str = ""
    description: str = ""
    amount: float
    payment_method: str = ""
    is_potential_duplicate: bool = False


class ImportPreview(BaseModel):
    """导入预览响应"""
    filename: str
    total_records: int
    preview_data: List[dict] = []
    detected_format: str = ""
    potential_duplicates: int = 0
    income_count: int = 0
    expense_count: int = 0
    date_range: Optional[dict] = None


class ImportErrorDetail(BaseModel):
    """导入错误详情"""
    row_number: int
    error_type: str
    error_message: str
    row_data: Optional[dict] = None


class ImportLogResponse(BaseModel):
    """导入日志响应"""
    id: int
    source: str
    file_name: Optional[str] = None
    status: str
    total_records: int = 0
    success_records: int = 0
    failed_records: int = 0
    skipped_records: int = 0
    error_details: Optional[list] = None
    import_summary: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImportLogListResponse(BaseModel):
    """导入日志列表响应"""
    logs: List[ImportLogResponse]
    total: int


class ValidateResponse(BaseModel):
    """文件验证响应"""
    is_valid: bool
    message: str
    file_info: Optional[dict] = None
