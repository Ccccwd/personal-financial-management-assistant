"""
分析报告接口
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta
import calendar

from app.config.database import get_db
from app.schemas.common import Response
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.core.dependencies import get_current_active_user

router = APIRouter()


def get_month_date_range(year: int, month: int):
    """获取月份的开始和结束日期"""
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    return start_date, end_date


@router.get("/monthly", response_model=Response)
async def get_monthly_report(
    year: int = Query(..., ge=2020, le=2100, description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取月度报告"""
    start_date, end_date = get_month_date_range(year, month)

    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    net = total_income - total_expense
    days_in_month = calendar.monthrange(year, month)[1]
    daily_avg_expense = float(total_expense / days_in_month) if days_in_month > 0 else 0.0

    max_expense = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).order_by(Transaction.amount.desc()).first()

    max_expense_data = None
    if max_expense:
        max_expense_data = {
            "amount": float(max_expense.amount),
            "date": max_expense.transaction_date.strftime("%Y-%m-%d"),
            "category": max_expense.category.name if max_expense.category else "未分类",
            "remark": max_expense.remark
        }

    category_stats = db.query(
        Category.id, Category.name, Category.icon, Category.color,
        func.sum(Transaction.amount).label("total_amount"),
        func.count(Transaction.id).label("transaction_count")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(
        Category.id, Category.name, Category.icon, Category.color
    ).order_by(func.sum(Transaction.amount).desc()).limit(5).all()

    top_categories = []
    for cat_id, name, icon, color, amount, count in category_stats:
        percentage = float((amount / total_expense) * 100) if total_expense > 0 else 0.0
        top_categories.append({
            "id": cat_id, "name": name, "icon": icon, "color": color,
            "amount": float(amount), "count": count, "percentage": round(percentage, 2)
        })

    return Response(code=200, message="success", data={
        "period": f"{year}-{month:02d}",
        "summary": {
            "total_income": float(total_income), "total_expense": float(total_expense),
            "net": float(net), "daily_avg_expense": round(daily_avg_expense, 2)
        },
        "max_expense": max_expense_data,
        "top_categories": top_categories
    })


@router.get("/yearly", response_model=Response)
async def get_yearly_report(
    year: int = Query(..., ge=2020, le=2100, description="年份"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取年度报告"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    net = total_income - total_expense

    monthly_trend = []
    for m in range(1, 13):
        ms, me = get_month_date_range(year, m)
        mi = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id, Transaction.type == "income",
            Transaction.transaction_date >= ms, Transaction.transaction_date <= me
        ).scalar() or Decimal("0")
        me_val = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id, Transaction.type == "expense",
            Transaction.transaction_date >= ms, Transaction.transaction_date <= me
        ).scalar() or Decimal("0")
        monthly_trend.append({
            "month": m, "income": float(mi), "expense": float(me_val), "net": float(mi - me_val)
        })

    return Response(code=200, message="success", data={
        "period": str(year),
        "summary": {
            "total_income": float(total_income), "total_expense": float(total_expense),
            "net": float(net), "transaction_count": 0
        },
        "monthly_trend": monthly_trend,
        "top_categories": []
    })


@router.get("/category/{category_id}", response_model=Response)
async def get_category_analysis(
    category_id: int = Path(..., description="分类ID"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分类分析"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return Response(code=404, message="分类不存在", data=None)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == category_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).order_by(Transaction.transaction_date.desc()).all()

    amounts = [float(t.amount) for t in transactions]
    total_amount = sum(amounts) if amounts else 0
    count = len(amounts)

    daily_trend = {}
    for t in transactions:
        dk = t.transaction_date.strftime("%Y-%m-%d")
        if dk not in daily_trend:
            daily_trend[dk] = {"date": dk, "amount": 0.0, "count": 0}
        daily_trend[dk]["amount"] += float(t.amount)
        daily_trend[dk]["count"] += 1

    return Response(code=200, message="success", data={
        "category": {
            "id": category.id, "name": category.name,
            "icon": category.icon, "color": category.color, "type": category.type
        },
        "period": f"最近{days}天",
        "total_amount": round(total_amount, 2),
        "transaction_count": count,
        "avg_amount": round(total_amount / count, 2) if count > 0 else 0.0,
        "max_amount": round(max(amounts), 2) if amounts else 0.0,
        "min_amount": round(min(amounts), 2) if amounts else 0.0,
        "daily_trend": sorted(daily_trend.values(), key=lambda x: x["date"])
    })


@router.post("/monthly-auto-report", response_model=Response)
async def generate_monthly_auto_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """生成月度自动报告"""
    now = datetime.now()
    task_id = f"report_{current_user.id}_{now.year}_{now.month}_{int(now.timestamp())}"

    return Response(code=200, message="报告生成任务已创建", data={
        "task_id": task_id, "status": "pending",
        "period": f"{now.year}-{now.month:02d}",
        "message": "月度报告正在生成中",
        "created_at": now.isoformat()
    })
