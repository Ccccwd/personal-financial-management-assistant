"""
提醒相关 Schema
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ReminderBase(BaseModel):
    """提醒基础 Schema"""
    type: str = Field(..., description="提醒类型: daily/budget/recurring/report")
    title: str = Field(..., min_length=1, max_length=100, description="提醒标题")
    content: Optional[str] = Field(None, max_length=500, description="提醒内容")
    remind_time: Optional[str] = Field(None, description="提醒时间 格式: HH:MM:SS")
    remind_day: Optional[int] = Field(None, ge=1, le=31, description="提醒日期(1-31)")
    category_id: Optional[int] = Field(None, description="分类ID")
    amount: Optional[Decimal] = Field(None, ge=0, description="金额阈值")
    is_enabled: bool = Field(default=True, description="是否启用")


class ReminderCreate(ReminderBase):
    """提醒创建 Schema"""
    pass


class ReminderUpdate(BaseModel):
    """提醒更新 Schema (部分更新)"""
    type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, max_length=500)
    remind_time: Optional[str] = None
    remind_day: Optional[int] = Field(None, ge=1, le=31)
    category_id: Optional[int] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    is_enabled: Optional[bool] = None


class ReminderResponse(ReminderBase):
    """提醒响应 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_reminded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReminderStatistics(BaseModel):
    """提醒统计 Schema"""
    total: int = Field(description="提醒总数")
    enabled: int = Field(description="启用数量")
    disabled: int = Field(description="禁用数量")


class ReminderListResponse(BaseModel):
    """提醒列表响应 Schema"""
    reminders: list[ReminderResponse]
    total: int
