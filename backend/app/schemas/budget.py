"""
预算相关 Schema
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class BudgetBase(BaseModel):
    """预算基础 Schema"""
    category_id: Optional[int] = Field(None, description="分类ID，null表示总预算")
    amount: Decimal = Field(..., gt=0, description="预算金额")
    period_type: str = Field(default="monthly", description="周期类型: monthly/yearly")
    year: int = Field(..., ge=2020, le=2100, description="年份")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份")
    alert_threshold: int = Field(default=80, ge=0, le=100, description="预警阈值百分比")
    is_enabled: bool = Field(default=True, description="是否启用")


class BudgetCreate(BudgetBase):
    """预算创建 Schema"""
    pass


class BudgetUpdate(BaseModel):
    """预算更新 Schema (部分更新)"""
    category_id: Optional[int] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    period_type: Optional[str] = None
    year: Optional[int] = Field(None, ge=2020, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    alert_threshold: Optional[int] = Field(None, ge=0, le=100)
    is_enabled: Optional[bool] = None


class BudgetResponse(BudgetBase):
    """预算响应 Schema"""
    id: int

    class Config:
        from_attributes = True


class BudgetWithProgress(BudgetResponse):
    """带进度信息的预算响应 Schema"""
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    category_type: Optional[str] = None
    actual_spending: Decimal = Field(description="实际支出")
    remaining: Decimal = Field(description="剩余预算")
    percentage: float = Field(description="使用百分比")
    status: str = Field(description="状态: normal/warning/exceeded")


class BudgetListResponse(BaseModel):
    """预算列表响应 Schema"""
    year: int
    month: Optional[int] = None
    budgets: List[BudgetWithProgress]
    total: int
