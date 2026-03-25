"""
分类相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """分类基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: str = Field(default="expense", description="分类类型: income/expense")
    icon: Optional[str] = Field(None, max_length=10, description="图标")
    color: Optional[str] = Field(None, max_length=7, description="颜色")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(default=0, ge=0, description="排序序号")


class CategoryCreate(CategoryBase):
    """分类创建 Schema"""
    pass


class CategoryUpdate(BaseModel):
    """分类更新 Schema (部分更新)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=7)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = Field(None, ge=0)


class CategoryResponse(BaseModel):
    """分类响应 Schema"""
    id: int
    name: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_system: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryTreeResponse(CategoryResponse):
    """分类树响应 Schema (含子分类)"""
    children: List["CategoryTreeResponse"] = []

    class Config:
        from_attributes = True


class CategoryStatsItem(CategoryResponse):
    """带统计信息的分类 Schema"""
    transaction_count: int = 0
    total_amount: float = 0.0


class CategoryListResponse(BaseModel):
    """分类列表响应 Schema"""
    categories: List[CategoryResponse]
    total: int


# 解决递归引用
CategoryTreeResponse.model_rebuild()
