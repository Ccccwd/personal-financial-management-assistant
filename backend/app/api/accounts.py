"""
账户管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime
from typing import Optional

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.account import (
    AccountCreate, AccountUpdate, AccountResponse,
    AccountListResponse, AccountSummaryResponse,
    TransferRequest, TransferResponse, BalanceAdjustRequest
)
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=Response)
async def get_accounts(
    type: Optional[str] = Query(None, description="账户类型"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取账户列表

    返回当前用户的所有账户，可按类型和启用状态过滤。
    """
    query = db.query(Account).filter(Account.user_id == current_user.id)

    if type:
        query = query.filter(Account.type == type)

    if is_enabled is not None:
        query = query.filter(Account.is_enabled == is_enabled)

    accounts = query.order_by(Account.is_default.desc(), Account.id).all()

    return Response(
        code=200,
        message="success",
        data=AccountListResponse(
            accounts=[AccountResponse.model_validate(a) for a in accounts],
            total=len(accounts)
        ).model_dump()
    )


@router.get("/summary", response_model=Response)
async def get_account_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取账户统计摘要

    返回总资产和各账户余额分布。
    """
    accounts = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_enabled == True
    ).all()

    total_balance = sum(float(a.balance) for a in accounts)

    # 按账户类型分组统计
    type_distribution = {}
    for account in accounts:
        if account.type not in type_distribution:
            type_distribution[account.type] = {
                "type": account.type,
                "balance": 0.0,
                "count": 0
            }
        type_distribution[account.type]["balance"] += float(account.balance)
        type_distribution[account.type]["count"] += 1

    distribution_list = list(type_distribution.values())

    return Response(
        code=200,
        message="success",
        data=AccountSummaryResponse(
            total_balance=Decimal(str(total_balance)),
            total_accounts=len(accounts),
            account_distribution=distribution_list
        ).model_dump()
    )


@router.get("/default", response_model=Response)
async def get_default_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取默认账户

    返回用户设置的默认账户，如果没有则返回第一个启用的账户。
    """
    # 优先查找默认账户
    account = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_default == True,
        Account.is_enabled == True
    ).first()

    # 如果没有默认账户，返回第一个启用的账户
    if not account:
        account = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.is_enabled == True
        ).first()

    if not account:
        return Response(code=404, message="没有可用的账户", data=None)

    return Response(
        code=200,
        message="success",
        data=AccountResponse.model_validate(account).model_dump()
    )


@router.get("/{account_id}", response_model=Response)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取账户详情

    返回账户基本信息及该账户的收支统计。
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    # 统计该账户的收支情况
    income_total = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.account_id == account_id,
        Transaction.type == "income"
    ).scalar() or 0

    expense_total = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.account_id == account_id,
        Transaction.type == "expense"
    ).scalar() or 0

    account_dict = AccountResponse.model_validate(account).model_dump()
    account_dict["income_total"] = float(income_total)
    account_dict["expense_total"] = float(expense_total)

    return Response(
        code=200,
        message="success",
        data=account_dict
    )


@router.post("", response_model=Response)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建账户

    创建新账户，初始余额默认作为账户的当前余额。
    """
    # 检查同名账户是否已存在
    existing = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.name == account_data.name
    ).first()

    if existing:
        return Response(code=400, message="该账户名称已存在", data=None)

    # 如果设置为默认账户，需要取消其他账户的默认状态
    if account_data.is_default:
        db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.is_default == True
        ).update({"is_default": False})

    account = Account(
        user_id=current_user.id,
        name=account_data.name,
        type=account_data.type,
        balance=account_data.initial_balance,
        initial_balance=account_data.initial_balance,
        icon=account_data.icon,
        color=account_data.color,
        is_default=account_data.is_default,
        description=account_data.description,
        is_enabled=True
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return Response(
        code=200,
        message="创建成功",
        data=AccountResponse.model_validate(account).model_dump()
    )


@router.put("/{account_id}", response_model=Response)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新账户

    支持部分字段更新。注意：余额不能通过此接口修改，请使用 adjust-balance。
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    # 如果设置为默认账户，需要取消其他账户的默认状态
    if account_data.is_default:
        db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.is_default == True,
            Account.id != account_id
        ).update({"is_default": False})

    # 更新字段
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)

    return Response(
        code=200,
        message="更新成功",
        data=AccountResponse.model_validate(account).model_dump()
    )


@router.delete("/{account_id}", response_model=Response)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除账户

    有交易记录的账户不允许删除。
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    # 检查是否有关联的交易记录
    transactions_count = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).count()

    if transactions_count > 0:
        return Response(code=400, message="该账户下有交易记录，无法删除", data=None)

    db.delete(account)
    db.commit()

    return Response(
        code=200,
        message="删除成功",
        data=None
    )


@router.post("/transfer", response_model=Response)
async def transfer_between_accounts(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    账户间转账

    创建一条转出交易和一条转入交易，并更新两个账户的余额。
    """
    # 验证转出账户
    from_account = db.query(Account).filter(
        Account.id == transfer_data.from_account_id,
        Account.user_id == current_user.id
    ).first()

    if not from_account:
        return Response(code=404, message="转出账户不存在", data=None)

    # 验证转入账户
    to_account = db.query(Account).filter(
        Account.id == transfer_data.to_account_id,
        Account.user_id == current_user.id
    ).first()

    if not to_account:
        return Response(code=404, message="转入账户不存在", data=None)

    # 检查是否是同一个账户
    if transfer_data.from_account_id == transfer_data.to_account_id:
        return Response(code=400, message="不能向同一账户转账", data=None)

    # 检查余额是否充足
    if from_account.balance < transfer_data.amount:
        return Response(code=400, message="转出账户余额不足", data=None)

    # 获取转账时间
    transfer_time = transfer_data.transaction_date or datetime.now()

    # 创建转出交易
    from_transaction = Transaction(
        user_id=current_user.id,
        type="transfer",
        amount=transfer_data.amount,
        account_id=transfer_data.from_account_id,
        to_account_id=transfer_data.to_account_id,
        transaction_date=transfer_time,
        remark=transfer_data.remark or "账户转账",
        source="manual"
    )

    # 创建转入交易
    to_transaction = Transaction(
        user_id=current_user.id,
        type="transfer",
        amount=transfer_data.amount,
        account_id=transfer_data.to_account_id,
        to_account_id=transfer_data.from_account_id,
        transaction_date=transfer_time,
        remark=transfer_data.remark or "账户转账",
        source="manual"
    )

    # 更新账户余额
    from_account.balance -= transfer_data.amount
    to_account.balance += transfer_data.amount

    db.add(from_transaction)
    db.add(to_transaction)
    db.commit()

    # 刷新数据
    db.refresh(from_transaction)
    db.refresh(to_transaction)
    db.refresh(from_account)
    db.refresh(to_account)

    return Response(
        code=200,
        message="转账成功",
        data=TransferResponse(
            from_transaction={
                "id": from_transaction.id,
                "type": from_transaction.type,
                "amount": float(from_transaction.amount),
                "account_id": from_transaction.account_id,
                "to_account_id": from_transaction.to_account_id
            },
            to_transaction={
                "id": to_transaction.id,
                "type": to_transaction.type,
                "amount": float(to_transaction.amount),
                "account_id": to_transaction.account_id,
                "to_account_id": to_transaction.to_account_id
            },
            from_account_balance=from_account.balance,
            to_account_balance=to_account.balance
        ).model_dump()
    )


@router.post("/{account_id}/adjust-balance", response_model=Response)
async def adjust_account_balance(
    account_id: int,
    adjust_data: BalanceAdjustRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    调整账户余额

    手动校正账户余额，会创建一条调整记录。
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    old_balance = account.balance
    difference = adjust_data.new_balance - old_balance

    # 创建调整交易记录
    adjustment_type = "income" if difference > 0 else "expense"
    adjustment_transaction = Transaction(
        user_id=current_user.id,
        type=adjustment_type,
        amount=abs(difference),
        account_id=account_id,
        transaction_date=datetime.now(),
        remark=adjust_data.remark or "余额调整",
        source="manual"
    )

    # 更新账户余额
    account.balance = adjust_data.new_balance

    db.add(adjustment_transaction)
    db.commit()

    db.refresh(account)

    return Response(
        code=200,
        message="余额调整成功",
        data={
            "account": AccountResponse.model_validate(account).model_dump(),
            "old_balance": float(old_balance),
            "new_balance": float(adjust_data.new_balance),
            "difference": float(difference)
        }
    )


@router.get("/{account_id}/balance-history", response_model=Response)
async def get_account_balance_history(
    account_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    change_type: Optional[str] = Query(None, description="变动类型过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定账户的余额变动历史

    查询指定账户的交易记录作为余额变动历史。
    """
    # 验证账户存在
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    # 构建查询
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.account_id == account_id
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
            "account": {
                "id": account.id,
                "name": account.name,
                "type": account.type,
                "current_balance": float(account.balance)
            },
            "items": history_items,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )
