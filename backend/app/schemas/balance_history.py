"""
余额历史相关 Schema
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class BalanceHistoryResponse(BaseModel):
    """余额历史响应 Schema"""
    id: int
    account_id: int
    account_name: Optional[str] = Field(None, description="账户名称")
    transaction_id: Optional[int] = None
    change_type: str = Field(..., description="变化类型: income/expense/transfer/adjust")
    amount_before: Decimal = Field(..., description="变化前余额")
    amount_after: Decimal = Field(..., description="变化后余额")
    change_amount: Decimal = Field(..., description="变化金额")
    description: Optional[str] = None
    created_at: datetime = Field(..., description="记录时间")

    class Config:
        from_attributes = True


class BalanceHistoryListResponse(BaseModel):
    """余额历史列表响应 Schema"""
    items: list[BalanceHistoryResponse]
    total: int
    limit: int
    offset: int
