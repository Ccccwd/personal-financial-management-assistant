"""
预算管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime
from typing import Optional
import calendar

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse
)
from app.models.user import User
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.dependencies import get_current_active_user

router = APIRouter()


def calculate_budget_progress(
    db: Session,
    budget: Budget,
    user_id: int
) -> dict:
    """
    计算预算进度

    返回实际支出、剩余金额、使用百分比和状态
    """
    # 确定日期范围
    if budget.period_type == "monthly":
        if budget.month:
            # 特定月份
            start_date = datetime(budget.year, budget.month, 1)
            last_day = calendar.monthrange(budget.year, budget.month)[1]
            end_date = datetime(budget.year, budget.month, last_day, 23, 59, 59)
        else:
            # 当年所有月份（不常用）
            start_date = datetime(budget.year, 1, 1)
            end_date = datetime(budget.year, 12, 31, 23, 59, 59)
    else:  # yearly
        start_date = datetime(budget.year, 1, 1)
        end_date = datetime(budget.year, 12, 31, 23, 59, 59)

    # 构建查询
    query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    )

    # 如果是分类预算，添加分类过滤
    if budget.category_id:
        query = query.filter(Transaction.category_id == budget.category_id)

    actual_spending = query.scalar() or Decimal("0")

    # 计算剩余和百分比
    remaining = budget.amount - actual_spending
    percentage = 0.0
    if budget.amount > 0:
        percentage = float((actual_spending / budget.amount) * 100)

    # 确定状态
    if percentage >= 100:
        status = "exceeded"
    elif percentage >= budget.alert_threshold:
        status = "warning"
    else:
        status = "normal"

    return {
        "actual_spending": actual_spending,
        "remaining": remaining,
        "percentage": round(percentage, 2),
        "status": status
    }


@router.get("", response_model=Response)
async def get_budgets(
    year: int = Query(..., ge=2020, le=2100, description="年份"),
    month: Optional[int] = Query(None, ge=1, le=12, description="月份"),
    period_type: Optional[str] = Query(None, description="周期类型"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取预算列表

    返回指定年份/月份的预算，包含实时进度计算。
    """
    query = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.year == year
    )

    if month is not None:
        query = query.filter(Budget.month == month)

    if period_type:
        query = query.filter(Budget.period_type == period_type)

    budgets = query.order_by(Budget.id).all()

    # 计算每个预算的进度
    result = []
    for budget in budgets:
        data = BudgetResponse.model_validate(budget).model_dump()

        # 添加分类信息
        if budget.category:
            data["category_name"] = budget.category.name
            data["category_icon"] = budget.category.icon
            data["category_type"] = budget.category.type
        else:
            data["category_name"] = None
            data["category_icon"] = None
            data["category_type"] = None

        # 计算进度
        progress = calculate_budget_progress(db, budget, current_user.id)
        data.update(progress)

        result.append(data)

    return Response(
        code=200,
        message="success",
        data={
            "year": year,
            "month": month,
            "budgets": result,
            "total": len(result)
        }
    )


@router.post("", response_model=Response)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建预算

    检查唯一性：同一用户、同一周期、同一分类只能有一个预算。
    """
    # 如果指定了分类，验证分类存在
    if budget_data.category_id:
        category = db.query(Category).filter(
            Category.id == budget_data.category_id
        ).first()
        if not category:
            return Response(code=404, message="分类不存在", data=None)

    # 检查唯一性
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.year == budget_data.year,
        Budget.period_type == budget_data.period_type,
        Budget.month == budget_data.month,
        Budget.category_id == budget_data.category_id
    ).first()

    if existing:
        return Response(code=400, message="该周期已存在相同分类的预算", data=None)

    budget = Budget(
        user_id=current_user.id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        period_type=budget_data.period_type,
        year=budget_data.year,
        month=budget_data.month,
        alert_threshold=budget_data.alert_threshold,
        is_enabled=budget_data.is_enabled
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return Response(
        code=200,
        message="创建成功",
        data=BudgetResponse.model_validate(budget).model_dump()
    )


@router.get("/{budget_id}", response_model=Response)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取预算详情

    返回预算信息和使用进度。
    """
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        return Response(code=404, message="预算不存在", data=None)

    data = BudgetResponse.model_validate(budget).model_dump()

    # 添加分类信息
    if budget.category:
        data["category_name"] = budget.category.name
        data["category_icon"] = budget.category.icon
        data["category_type"] = budget.category.type
    else:
        data["category_name"] = None
        data["category_icon"] = None
        data["category_type"] = None

    # 计算进度
    progress = calculate_budget_progress(db, budget, current_user.id)
    data.update(progress)

    return Response(
        code=200,
        message="success",
        data=data
    )


@router.put("/{budget_id}", response_model=Response)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新预算

    支持部分字段更新。
    """
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        return Response(code=404, message="预算不存在", data=None)

    # 更新字段
    update_data = budget_data.model_dump(exclude_unset=True)

    # 如果修改了唯一性约束字段，检查冲突
    if any(k in update_data for k in ["year", "month", "period_type", "category_id"]):
        check_year = update_data.get("year", budget.year)
        check_month = update_data.get("month", budget.month)
        check_period = update_data.get("period_type", budget.period_type)
        check_category = update_data.get("category_id", budget.category_id)

        existing = db.query(Budget).filter(
            Budget.user_id == current_user.id,
            Budget.year == check_year,
            Budget.month == check_month,
            Budget.period_type == check_period,
            Budget.category_id == check_category,
            Budget.id != budget_id
        ).first()

        if existing:
            return Response(code=400, message="该周期已存在相同分类的预算", data=None)

    for field, value in update_data.items():
        setattr(budget, field, value)

    db.commit()
    db.refresh(budget)

    return Response(
        code=200,
        message="更新成功",
        data=BudgetResponse.model_validate(budget).model_dump()
    )


@router.delete("/{budget_id}", response_model=Response)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除预算
    """
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        return Response(code=404, message="预算不存在", data=None)

    db.delete(budget)
    db.commit()

    return Response(
        code=200,
        message="删除成功",
        data=None
    )
