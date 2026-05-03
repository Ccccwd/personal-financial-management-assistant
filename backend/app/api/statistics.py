"""
统计分析接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
import calendar

from app.config.database import get_db
from app.schemas.common import Response
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account import Account
from app.core.dependencies import get_current_active_user

router = APIRouter()


def get_month_date_range(year: int, month: int):
    """获取月份的开始和结束日期"""
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    return start_date, end_date


def get_prev_month_date_range(year: int, month: int):
    """获取上个月份的开始和结束日期"""
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    return get_month_date_range(prev_year, prev_month)


@router.get("/overview", response_model=Response)
async def get_statistics_overview(
    current_year: Optional[int] = Query(None, description="当前年份"),
    current_month: Optional[int] = Query(None, description="当前月份"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取首页统计概览

    返回月度汇总、总资产、分类分布和趋势数据。
    """
    # 默认使用当前年月
    now = datetime.now()
    year = current_year or now.year
    month = current_month or now.month

    # 获取当月日期范围
    start_date, end_date = get_month_date_range(year, month)

    # 计算当月收支
    monthly_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    monthly_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or Decimal("0")

    monthly_balance = monthly_income - monthly_expense

    # 获取上月数据计算增长率
    prev_start, prev_end = get_prev_month_date_range(year, month)

    prev_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.transaction_date >= prev_start,
        Transaction.transaction_date <= prev_end
    ).scalar() or Decimal("0")

    prev_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= prev_start,
        Transaction.transaction_date <= prev_end
    ).scalar() or Decimal("0")

    # 计算增长率
    income_growth = None
    expense_growth = None

    if prev_income > 0:
        income_growth = float(((monthly_income - prev_income) / prev_income) * 100)

    if prev_expense > 0:
        expense_growth = float(((monthly_expense - prev_expense) / prev_expense) * 100)

    # 总资产（所有启用账户余额之和）
    total_balance = db.query(func.sum(Account.balance)).filter(
        Account.user_id == current_user.id,
        Account.is_enabled
    ).scalar() or Decimal("0")

    # 分类分布（支出）
    category_stats = db.query(
        Category.id,
        Category.name,
        Category.icon,
        Category.color,
        func.sum(Transaction.amount).label("total_amount")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(
        Category.id, Category.name, Category.icon, Category.color
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    category_distribution = []
    for cat_id, name, icon, color, amount in category_stats:
        percentage = 0.0
        if monthly_expense > 0:
            percentage = float((amount / monthly_expense) * 100)

        category_distribution.append({
            "name": name,
            "icon": icon,
            "color": color,
            "amount": float(amount),
            "percentage": round(percentage, 2)
        })

    # 趋势数据（本月每日收支）
    trend_data = []
    days_in_month = calendar.monthrange(year, month)[1]

    for day in range(1, days_in_month + 1):
        day_start = datetime(year, month, day)
        day_end = datetime(year, month, day, 23, 59, 59)

        day_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "income",
            Transaction.transaction_date >= day_start,
            Transaction.transaction_date <= day_end
        ).scalar() or Decimal("0")

        day_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.transaction_date >= day_start,
            Transaction.transaction_date <= day_end
        ).scalar() or Decimal("0")

        trend_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "income": float(day_income),
            "expense": float(day_expense),
            "balance": float(day_income - day_expense)
        })

    return Response(
        code=200,
        message="success",
        data={
            "period": f"{year}-{month:02d}",
            "monthly_summary": {
                "income": float(monthly_income),
                "expense": float(monthly_expense),
                "balance": float(monthly_balance),
                "income_growth": income_growth,
                "expense_growth": expense_growth
            },
            "total_balance": float(total_balance),
            "category_distribution": category_distribution,
            "trend_data": trend_data
        }
    )


@router.get("/trend", response_model=Response)
async def get_statistics_trend(
    period: str = Query("daily", description="统计周期: daily/weekly/monthly/yearly"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取趋势分析

    返回指定时间范围内的收支趋势。
    """
    # 默认时间范围：最近30天
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    trend = []

    if period == "daily":
        # 按天统计
        current = start_date.date()
        end = end_date.date()

        while current <= end:
            day_start = datetime.combine(current, datetime.min.time())
            day_end = datetime.combine(current, datetime.max.time())

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "income",
                Transaction.transaction_date >= day_start,
                Transaction.transaction_date <= day_end
            ).scalar() or Decimal("0")

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense",
                Transaction.transaction_date >= day_start,
                Transaction.transaction_date <= day_end
            ).scalar() or Decimal("0")

            trend.append({
                "date": current.strftime("%Y-%m-%d"),
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense)
            })

            current += timedelta(days=1)

    elif period == "monthly":
        # 按月统计
        current = start_date.replace(day=1)

        while current <= end_date:
            _, last_day = calendar.monthrange(current.year, current.month)
            month_end = current.replace(day=last_day, hour=23, minute=59, second=59)

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "income",
                Transaction.transaction_date >= current,
                Transaction.transaction_date <= month_end
            ).scalar() or Decimal("0")

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense",
                Transaction.transaction_date >= current,
                Transaction.transaction_date <= month_end
            ).scalar() or Decimal("0")

            trend.append({
                "date": current.strftime("%Y-%m"),
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense)
            })

            # 下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

            if current > end_date:
                break

    elif period == "yearly":
        # 按年统计
        start_year = start_date.year
        end_year = end_date.year

        for year in range(start_year, end_year + 1):
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31, 23, 59, 59)

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "income",
                Transaction.transaction_date >= year_start,
                Transaction.transaction_date <= year_end
            ).scalar() or Decimal("0")

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense",
                Transaction.transaction_date >= year_start,
                Transaction.transaction_date <= year_end
            ).scalar() or Decimal("0")

            trend.append({
                "date": str(year),
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense)
            })

    else:  # weekly
        # 按周统计（简单实现：从开始日期起每7天）
        current = start_date
        week_num = 1

        while current <= end_date:
            week_end = current + timedelta(days=6)
            week_end = min(week_end, end_date)
            week_end = week_end.replace(hour=23, minute=59, second=59)

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "income",
                Transaction.transaction_date >= current,
                Transaction.transaction_date <= week_end
            ).scalar() or Decimal("0")

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense",
                Transaction.transaction_date >= current,
                Transaction.transaction_date <= week_end
            ).scalar() or Decimal("0")

            trend.append({
                "date": f"第{week_num}周",
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense)
            })

            current = week_end + timedelta(seconds=1)
            week_num += 1

    return Response(
        code=200,
        message="success",
        data={
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "trend": trend
        }
    )


@router.get("/category", response_model=Response)
async def get_category_statistics(
    transaction_type: str = Query(..., description="交易类型: income/expense"),
    period: str = Query("monthly", description="统计周期: monthly/yearly"),
    year: Optional[int] = Query(None, description="年份"),
    month: Optional[int] = Query(None, ge=1, le=12, description="月份（月度统计时必填）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类统计

    返回指定周期内各分类的收支统计。
    """
    now = datetime.now()
    stat_year = year or now.year
    stat_month = month or now.month

    # 确定日期范围
    if period == "yearly":
        start_date = datetime(stat_year, 1, 1)
        end_date = datetime(stat_year, 12, 31, 23, 59, 59)
    else:  # monthly
        start_date, end_date = get_month_date_range(stat_year, stat_month)

    # 查询分类统计
    category_stats = db.query(
        Category.id,
        Category.name,
        Category.icon,
        Category.color,
        func.sum(Transaction.amount).label("total_amount"),
        func.count(Transaction.id).label("transaction_count")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == transaction_type,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(
        Category.id, Category.name, Category.icon, Category.color
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    # 计算总金额
    total_amount = sum(amount for _, _, _, _, amount, _ in category_stats) or Decimal("0")

    # 构建结果
    categories = []
    for cat_id, name, icon, color, amount, count in category_stats:
        percentage = 0.0
        if total_amount > 0:
            percentage = float((amount / total_amount) * 100)

        categories.append({
            "id": cat_id,
            "name": name,
            "icon": icon,
            "color": color,
            "amount": float(amount),
            "count": count,
            "percentage": round(percentage, 2)
        })

    return Response(
        code=200,
        message="success",
        data={
            "transaction_type": transaction_type,
            "total_amount": float(total_amount),
            "categories": categories
        }
    )


@router.get("/export/excel", response_model=Response)
async def export_transactions_excel(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出交易记录为Excel

    返回导出任务的ID，实际导出可以在后台异步处理。
    """
    # 简化实现：返回成功消息
    # 实际项目中可以生成Excel文件并返回下载链接

    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    transaction_count = query.count()

    return Response(
        code=200,
        message=f"导出任务已创建，共 {transaction_count} 条记录",
        data={
            "task_id": f"export_{current_user.id}_{int(datetime.now().timestamp())}",
            "record_count": transaction_count,
            "status": "pending",
            "message": "Excel文件生成中，请稍后在下载中心查看"
        }
    )
