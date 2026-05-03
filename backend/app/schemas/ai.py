"""
AI 服务相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ClassifyItem(BaseModel):
    """分类请求项"""
    merchant_name: str = Field(..., description="商户名称")
    product_name: Optional[str] = Field(None, description="商品名称")
    wechat_category: Optional[str] = Field(None, description="微信分类")
    amount: float = Field(..., ge=0, description="金额")
    transaction_type: str = Field(..., description="交易类型：expense/income")


class ClassifyRequest(BaseModel):
    """分类请求"""
    items: List[ClassifyItem] = Field(..., min_items=1, max_items=100, description="待分类的交易列表")


class ClassifyResultItem(BaseModel):
    """单条分类结果"""
    index: int = Field(..., description="原请求列表中的索引")
    merchant_name: str = Field(..., description="商户名称")
    category_id: Optional[int] = Field(None, description="分类ID")
    category_name: str = Field(..., description="分类名称")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    matched_by: str = Field(..., description="匹配方式：rule/llm")


class ClassifyResponse(BaseModel):
    """分类响应"""
    results: List[ClassifyResultItem] = Field(..., description="分类结果列表")
    total: int = Field(..., description="总数")
    llm_called_count: int = Field(..., description="调用LLM次数")
    rule_matched_count: int = Field(..., description="规则匹配次数")


class AdviceResponse(BaseModel):
    """理财建议响应"""
    generated_at: datetime = Field(..., description="生成时间")
    from_cache: bool = Field(..., description="是否来自缓存")
    analysis_period: dict = Field(..., description="分析周期 {start, end}")
    advice: dict = Field(..., description="建议内容 {highlights, warnings, suggestions, next_month_budget, full_report}")


class AIUsageResponse(BaseModel):
    """用量统计响应"""
    month: str = Field(..., description="统计月份")
    classify_calls: int = Field(..., description="分类调用次数")
    advice_calls: int = Field(..., description="建议调用次数")
    total_tokens_used: int = Field(..., description="总消耗Token数")
