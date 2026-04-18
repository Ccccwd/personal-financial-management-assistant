"""
余额历史接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime

from app.config.database import get_db
from app.schemas.common import Response
from app.models.user import User
from app.models.transaction import Transaction
from app.models.account import Account
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=Response)
async def get_balance_history(
    limit: int = Query(100, ge=1, le=500, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    change_type: Optional[str] = Query(None, description="变动类型过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有账户余额历史

    查询当前用户所有交易记录，按时间排序，返回交易记录作为余额变动历史。
    """
    # 构建查询
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )

    # 按变动类型过滤
    if change_type:
        query = query.filter(Transaction.type == change_type)

    # 按时间倒序排序
    query = query.order_by(Transaction.transaction_date.desc())

    # 分页
    total = query.count()
    transactions = query.offset(offset).limit(limit).all()

    # 构建返回数据
    history_items = []
    for t in transactions:
        # 确定变动类型描述
        type_desc = {
            "income": "收入",
            "expense": "支出",
            "transfer": "转账",
            "adjustment": "调整"
        }.get(t.type, t.type)

        # 获取账户信息
        account = None
        if t.account:
            account = {
                "id": t.account.id,
                "name": t.account.name,
                "type": t.account.type
            }

        # 获取转入账户信息（转账类型）
        to_account = None
        if t.to_account and t.type == "transfer":
            to_account = {
                "id": t.to_account.id,
                "name": t.to_account.name,
                "type": t.to_account.type
            }

        history_items.append({
            "id": t.id,
            "transaction_date": t.transaction_date.isoformat(),
            "type": t.type,
            "type_desc": type_desc,
            "amount": float(t.amount),
            "account": account,
            "to_account": to_account,
            "category": {
                "id": t.category.id,
                "name": t.category.name,
                "icon": t.category.icon,
                "color": t.category.color
            } if t.category else None,
            "remark": t.remark,
            "merchant_name": t.merchant_name,
            "source": t.source,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })

    return Response(
        code=200,
        message="success",
        data={
            "items": history_items,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )
