"""
统计分析相关 Schema
"""
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class MonthlySummary(BaseModel):
    """月度汇总"""
    income: Decimal = Field(description="月收入")
    expense: Decimal = Field(description="月支出")
    balance: Decimal = Field(description="月结余")
    income_growth: Optional[float] = Field(None, description="收入增长率（相比上月）")
    expense_growth: Optional[float] = Field(None, description="支出增长率（相比上月）")


class CategoryDistribution(BaseModel):
    """分类分布"""
    name: str = Field(description="分类名称")
    icon: Optional[str] = Field(None, description="分类图标")
    color: Optional[str] = Field(None, description="分类颜色")
    amount: Decimal = Field(description="金额")
    percentage: float = Field(description="占比百分比")


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str = Field(description="日期")
    income: Decimal = Field(description="收入")
    expense: Decimal = Field(description="支出")
    balance: Decimal = Field(description="结余")


class OverviewResponse(BaseModel):
    """首页概览响应"""
    period: str = Field(description="统计周期")
    monthly_summary: MonthlySummary = Field(description="月度汇总")
    total_balance: Decimal = Field(description="总资产")
    category_distribution: List[CategoryDistribution] = Field(description="分类分布")
    trend_data: List[TrendDataPoint] = Field(description="趋势数据")


class TrendResponse(BaseModel):
    """趋势分析响应"""
    period: str = Field(description="统计周期: daily/weekly/monthly/yearly")
    start_date: datetime = Field(description="开始日期")
    end_date: datetime = Field(description="结束日期")
    trend: List[TrendDataPoint] = Field(description="趋势数据列表")


class CategoryStatsItem(BaseModel):
    """分类统计项"""
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    amount: Decimal = Field(description="总金额")
    count: int = Field(description="交易笔数")
    percentage: float = Field(description="占比百分比")


class CategoryStatsResponse(BaseModel):
    """分类统计响应"""
    transaction_type: str = Field(description="交易类型: income/expense")
    total_amount: Decimal = Field(description="总金额")
    categories: List[CategoryStatsItem] = Field(description="分类统计列表")
