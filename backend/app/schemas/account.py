"""
账户相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    """账户基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="账户名称")
    type: str = Field(default="other", description="账户类型: cash/bank/wechat/alipay/meal_card/other")
    icon: Optional[str] = Field(None, max_length=10, description="图标")
    color: Optional[str] = Field(None, max_length=7, description="颜色")
    is_default: bool = Field(default=False, description="是否默认账户")
    description: Optional[str] = Field(None, description="账户描述")


class AccountCreate(AccountBase):
    """账户创建 Schema"""
    initial_balance: Decimal = Field(default=Decimal("0.00"), description="初始余额")


class AccountUpdate(BaseModel):
    """账户更新 Schema (部分更新)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=7)
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None


class AccountResponse(AccountBase):
    """账户响应 Schema"""
    id: int
    balance: Decimal = Field(description="当前余额")
    initial_balance: Decimal = Field(description="初始余额")
    is_enabled: bool = Field(description="是否启用")
    created_at: datetime

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """账户列表响应 Schema"""
    accounts: List[AccountResponse]
    total: int


class AccountSummaryResponse(BaseModel):
    """账户统计摘要响应 Schema"""
    total_balance: Decimal = Field(description="总资产")
    total_accounts: int = Field(description="账户总数")
    account_distribution: List[dict] = Field(default_factory=list, description="各账户余额分布")


class TransferRequest(BaseModel):
    """账户转账请求 Schema"""
    from_account_id: int = Field(..., description="转出账户ID")
    to_account_id: int = Field(..., description="转入账户ID")
    amount: Decimal = Field(..., gt=0, description="转账金额")
    remark: Optional[str] = Field(None, description="转账备注")
    transaction_date: Optional[datetime] = Field(None, description="转账时间")


class TransferResponse(BaseModel):
    """账户转账响应 Schema"""
    from_transaction: dict = Field(description="转出交易记录")
    to_transaction: dict = Field(description="转入交易记录")
    from_account_balance: Decimal = Field(description="转出账户余额")
    to_account_balance: Decimal = Field(description="转入账户余额")


class BalanceAdjustRequest(BaseModel):
    """余额调整请求 Schema"""
    new_balance: Decimal = Field(..., description="调整后余额")
    remark: Optional[str] = Field(None, description="调整原因")
