"""
交易记录相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """交易记录基础 Schema"""
    type: str = Field(..., description="交易类型: income/expense/transfer")
    amount: Decimal = Field(..., gt=0, description="交易金额，必须大于0")
    category_id: Optional[int] = Field(None, description="分类ID")
    account_id: int = Field(..., description="账户ID")
    to_account_id: Optional[int] = Field(None, description="转入账户ID（转账时必填）")
    transaction_date: datetime = Field(..., description="交易时间")
    remark: Optional[str] = Field(None, max_length=255, description="备注")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    product_name: Optional[str] = Field(None, max_length=255, description="商品名称")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    location: Optional[str] = Field(None, max_length=255, description="地理位置")
    images: Optional[List[str]] = Field(default_factory=list, description="图片URL列表")


class TransactionCreate(TransactionBase):
    """交易记录创建 Schema"""
    pass


class TransactionUpdate(BaseModel):
    """交易记录更新 Schema (部分更新)"""
    type: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    transaction_date: Optional[datetime] = None
    remark: Optional[str] = Field(None, max_length=255)
    merchant_name: Optional[str] = Field(None, max_length=100)
    product_name: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=255)
    images: Optional[List[str]] = None


class TransactionResponse(BaseModel):
    """交易记录响应 Schema"""
    id: int
    type: str
    amount: Decimal
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    account_id: int
    account_name: Optional[str] = None
    to_account_id: Optional[int] = None
    transaction_date: datetime
    remark: Optional[str] = None
    merchant_name: Optional[str] = None
    product_name: Optional[str] = None
    source: str
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    ai_classified: bool
    is_repeated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """交易记录列表响应 Schema"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TransactionSummaryResponse(BaseModel):
    """交易记录统计摘要响应 Schema"""
    total_income: Decimal = Field(description="总收入")
    total_expense: Decimal = Field(description="总支出")
    total_transfer: Decimal = Field(description="总转账")
    net_income: Decimal = Field(description="净收入（收入-支出）")
    transaction_count: int = Field(description="交易笔数")


class TransactionSearchItem(BaseModel):
    """交易记录搜索结果项"""
    id: int
    type: str
    amount: Decimal
    category_name: Optional[str] = None
    account_name: Optional[str] = None
    transaction_date: datetime
    remark: Optional[str] = None
    merchant_name: Optional[str] = None


class TransactionSearchResponse(BaseModel):
    """交易记录搜索响应 Schema"""
    results: List[TransactionSearchItem]
    total: int
