# API 开发剩余实现计划

## 概述

本文档记录了智能个人财务记账系统 API 开发的剩余任务，供后续实现参考。

## 已完成的工作

### 1. Schema 定义
- ✅ `backend/app/schemas/category.py` - 分类相关 Schema
- ✅ `backend/app/schemas/account.py` - 账户相关 Schema

### 2. API 端点实现
- ✅ `backend/app/api/categories.py` - 分类管理 API (7 个端点)
- ✅ `backend/app/api/accounts.py` - 账户管理 API (9 个端点)

### 3. OpenAPI 规范
- ✅ `docs/api.yaml` - 完整的 OpenAPI 3.0 规范文档

---

## 待完成的工作

### Phase 1: 剩余 Schema 定义

#### 1.1 交易相关 Schema (`backend/app/schemas/transaction.py`)

```python
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class TransactionBase(BaseModel):
    """交易基础 Schema"""
    type: str = Field(..., description="交易类型: income/expense/transfer")
    amount: Decimal = Field(..., gt=0, description="金额")
    category_id: Optional[int] = Field(None, description="分类ID")
    account_id: int = Field(..., description="账户ID")
    to_account_id: Optional[int] = Field(None, description="转入账户ID(转账)")
    transaction_date: datetime = Field(..., description="交易时间")
    remark: Optional[str] = Field(None, max_length=200, description="备注")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    product_name: Optional[str] = Field(None, max_length=100, description="商品名称")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    location: Optional[str] = Field(None, max_length=100, description="地理位置")
    images: Optional[List[str]] = Field(None, description="图片URL列表")

class TransactionCreate(TransactionBase):
    """交易创建 Schema"""
    pass

class TransactionUpdate(BaseModel):
    """交易更新 Schema (部分更新)"""
    type: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    transaction_date: Optional[datetime] = None
    remark: Optional[str] = Field(None, max_length=200)
    merchant_name: Optional[str] = Field(None, max_length=100)
    product_name: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None

class TransactionResponse(TransactionBase):
    """交易响应 Schema"""
    id: int
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    account_name: str
    source: str
    ai_classified: bool = False
    is_repeated: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    """交易列表响应 Schema"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class TransactionSummaryResponse(BaseModel):
    """交易统计摘要响应 Schema"""
    total_income: Decimal
    total_expense: Decimal
    total_transfer: Decimal
    net_income: Decimal
    transaction_count: int
```

#### 1.2 预算相关 Schema (`backend/app/schemas/budget.py`)

```python
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class BudgetBase(BaseModel):
    """预算基础 Schema"""
    category_id: Optional[int] = Field(None, description="分类ID(null为总预算)")
    amount: Decimal = Field(..., gt=0, description="预算金额")
    period_type: str = Field(default="monthly", description="周期类型: monthly/yearly")
    year: int = Field(..., ge=2020, le=2100, description="年份")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份")
    alert_threshold: int = Field(default=80, ge=1, le=100, description="预警阈值(%)")
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
    alert_threshold: Optional[int] = Field(None, ge=1, le=100)
    is_enabled: Optional[bool] = None

class CategoryInfo(BaseModel):
    """分类简要信息"""
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

class BudgetResponse(BudgetBase):
    """预算响应 Schema"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BudgetWithProgress(BudgetResponse):
    """带执行进度的预算响应 Schema"""
    category: Optional[CategoryInfo] = None
    actual_spending: Decimal = Decimal("0.00")
    remaining: Decimal = Decimal("0.00")
    percentage: float = 0.0
    status: str = "normal"  # normal/warning/exceeded

class BudgetListResponse(BaseModel):
    """预算列表响应 Schema"""
    year: int
    month: Optional[int] = None
    budgets: List[BudgetWithProgress]
```

#### 1.3 统计相关 Schema (`backend/app/schemas/statistics.py`)

```python
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

class MonthlySummary(BaseModel):
    """月度摘要"""
    income: Decimal
    expense: Decimal
    balance: Decimal
    income_growth: float = 0.0
    expense_growth: float = 0.0

class CategoryDistribution(BaseModel):
    """分类分布"""
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    amount: Decimal
    percentage: float

class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    income: Decimal = Decimal("0.00")
    expense: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")
    amount: Optional[Decimal] = None  # 用于单一趋势

class OverviewResponse(BaseModel):
    """首页概览响应 Schema"""
    period: str
    monthly_summary: MonthlySummary
    total_balance: Decimal
    category_distribution: List[CategoryDistribution]
    trend_data: List[TrendDataPoint]

class TrendResponse(BaseModel):
    """趋势数据响应 Schema"""
    period: str
    start_date: str
    end_date: str
    trend: List[TrendDataPoint]

class CategoryStatsItem(BaseModel):
    """分类统计项"""
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    amount: Decimal
    count: int
    percentage: float

class CategoryStatsResponse(BaseModel):
    """分类统计响应 Schema"""
    transaction_type: str
    total_amount: Decimal
    categories: List[CategoryStatsItem]
```

---

### Phase 2: 剩余 API 端点实现

#### 2.1 交易记录 API (`backend/app/api/transactions.py`)

**端点列表:**
1. `GET /api/transactions` - 获取交易列表(分页)
2. `GET /api/transactions/summary` - 获取统计摘要
3. `GET /api/transactions/search` - 搜索交易
4. `GET /api/transactions/{id}` - 获取交易详情
5. `POST /api/transactions` - 创建交易
6. `PUT /api/transactions/{id}` - 更新交易
7. `DELETE /api/transactions/{id}` - 删除交易
8. `POST /api/transactions/{id}/mark-repeated` - 标记重复

**关键业务逻辑:**

```python
# 创建交易时更新账户余额
if transaction.type == "income":
    account.balance += transaction.amount
elif transaction.type == "expense":
    account.balance -= transaction.amount

# 删除交易时恢复账户余额
if transaction.type == "income":
    account.balance -= transaction.amount
elif transaction.type == "expense":
    account.balance += transaction.amount
```

**查询参数:**
- `page`, `page_size` - 分页
- `type` - 交易类型
- `category_id`, `account_id` - 过滤
- `start_date`, `end_date` - 日期范围
- `keyword` - 关键词搜索
- `min_amount`, `max_amount` - 金额范围
- `sort_by`, `sort_order` - 排序

#### 2.2 预算管理 API (`backend/app/api/budgets.py`)

**端点列表:**
1. `GET /api/budgets` - 获取预算列表(含执行进度)
2. `POST /api/budgets` - 创建预算
3. `PUT /api/budgets/{id}` - 更新预算
4. `DELETE /api/budgets/{id}` - 删除预算

**关键业务逻辑:**

```python
# 计算预算执行进度
actual_spending = db.query(func.sum(Transaction.amount)).filter(
    Transaction.user_id == current_user.id,
    Transaction.type == "expense",
    Transaction.transaction_date >= period_start,
    Transaction.transaction_date <= period_end
).scalar() or 0

if budget.category_id:
    query = query.filter(Transaction.category_id == budget.category_id)

# 计算状态
percentage = (actual_spending / budget.amount) * 100
if percentage >= 100:
    status = "exceeded"
elif percentage >= budget.alert_threshold:
    status = "warning"
else:
    status = "normal"
```

#### 2.3 统计分析 API (`backend/app/api/statistics.py`)

**端点列表:**
1. `GET /api/statistics/overview` - 获取首页概览
2. `GET /api/statistics/trend` - 获取趋势数据
3. `GET /api/statistics/category` - 获取分类统计
4. `GET /api/statistics/export/excel` - 导出Excel

**关键业务逻辑:**

```python
# 计算环比增长率
def calculate_growth_rate(current: Decimal, previous: Decimal) -> float:
    if previous == 0:
        return 0.0
    return float((current - previous) / previous * 100)

# 按周期聚合趋势数据
if period == "daily":
    group_by = func.date(Transaction.transaction_date)
elif period == "weekly":
    group_by = func.strftime('%Y-%W', Transaction.transaction_date)
elif period == "monthly":
    group_by = func.strftime('%Y-%m', Transaction.transaction_date)
```

---

### Phase 3: API 测试

#### 3.1 测试配置 (`backend/tests/conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.config.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### 3.2 测试用例

每个模块的测试应包含:
- 测试成功创建
- 测试成功获取列表和详情
- 测试成功更新
- 测试成功删除
- 测试错误情况（未授权、资源不存在、参数校验失败）
- 测试业务逻辑（如：不能删除有交易的账户）

---

### Phase 4: 路由注册更新

在 `backend/app/api/__init__.py` 中添加:

```python
from . import transactions, budgets, statistics

api_router.include_router(transactions.router, prefix="/transactions", tags=["交易记录"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["预算管理"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])
```

---

## 验证方式

1. **启动服务:**
   ```bash
   cd backend
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **访问 API 文档:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **运行测试:**
   ```bash
   cd backend
   uv run pytest tests/ -v
   ```

4. **验证 API 功能:**
   - 使用 Postman 或 Apifox 导入 OpenAPI 文档
   - 测试各端点的请求和响应

---

## 注意事项

1. **响应格式统一:** 所有响应使用 `Response(code, message, data)` 格式
2. **认证依赖:** 使用 `get_current_active_user` 依赖注入
3. **错误处理:** 返回适当的 HTTP 状态码和错误消息
4. **数据库事务:** 确保多表操作使用事务
5. **余额联动:** 交易创建/删除时必须更新账户余额
6. **预算计算:** 查询时实时计算实际支出

---

## 参考资料

- 现有实现: `backend/app/api/auth.py`, `backend/app/api/categories.py`
- API 规范: `docs/api.md`, `docs/api.yaml`
- 数据模型: `backend/app/models/`
- 认证依赖: `backend/app/core/dependencies.py`
