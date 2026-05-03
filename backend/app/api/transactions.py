"""
交易记录管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from decimal import Decimal
from datetime import datetime
from typing import Optional

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionSummaryResponse
)
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account import Account
from app.core.dependencies import get_current_active_user

router = APIRouter()


def update_account_balance(
    db: Session,
    account: Account,
    amount: Decimal,
    transaction_type: str,
    is_reversal: bool = False
):
    """
    更新账户余额

    - is_reversal: True 表示回退操作（删除/更新交易时），金额符号取反
    """
    if is_reversal:
        amount = -amount

    if transaction_type == "income":
        account.balance += amount
    elif transaction_type == "expense":
        account.balance -= amount
    # transfer 类型由调用方处理两个账户


def get_transactions_query(
    db: Session,
    user_id: int,
    type_filter: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    keyword: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None
):
    """构建交易记录查询"""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if type_filter:
        query = query.filter(Transaction.type == type_filter)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    if account_id:
        query = query.filter(
            or_(
                Transaction.account_id == account_id,
                Transaction.to_account_id == account_id
            )
        )

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    if keyword:
        query = query.filter(
            or_(
                Transaction.remark.ilike(f"%{keyword}%"),
                Transaction.merchant_name.ilike(f"%{keyword}%"),
                Transaction.product_name.ilike(f"%{keyword}%")
            )
        )

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    return query


def enrich_transaction(transaction: Transaction) -> dict:
    """为交易记录添加关联信息"""
    data = TransactionResponse.model_validate(transaction).model_dump()

    # 添加分类名称和图标
    if transaction.category:
        data["category_name"] = transaction.category.name
        data["category_icon"] = transaction.category.icon
    else:
        data["category_name"] = None
        data["category_icon"] = None

    # 添加账户名称
    if transaction.account:
        data["account_name"] = transaction.account.name
    else:
        data["account_name"] = None

    return data


@router.get("", response_model=Response)
async def get_transactions(
    type: Optional[str] = Query(None, description="交易类型: income/expense/transfer"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    account_id: Optional[int] = Query(None, description="账户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    min_amount: Optional[Decimal] = Query(None, description="最小金额"),
    max_amount: Optional[Decimal] = Query(None, description="最大金额"),
    sort_by: str = Query("transaction_date", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向: asc/desc"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取交易记录列表（分页）

    支持多种筛选条件和排序。
    """
    query = get_transactions_query(
        db, current_user.id, type, category_id, account_id,
        start_date, end_date, keyword, min_amount, max_amount
    )

    # 排序
    sort_column = getattr(Transaction, sort_by, Transaction.transaction_date)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # 分页
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    transactions = query.offset(offset).limit(page_size).all()

    return Response(
        code=200,
        message="success",
        data={
            "transactions": [enrich_transaction(t) for t in transactions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/summary", response_model=Response)
async def get_transactions_summary(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    type: Optional[str] = Query(None, description="交易类型"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取交易记录统计摘要

    返回指定时间范围内的收支统计。
    """
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    # 总收入
    income_query = query.filter(Transaction.type == "income")
    total_income = income_query.with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")

    # 总支出
    expense_query = query.filter(Transaction.type == "expense")
    total_expense = expense_query.with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")

    # 总转账
    transfer_query = query.filter(Transaction.type == "transfer")
    total_transfer = transfer_query.with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")

    # 交易笔数
    transaction_count = query.count()

    # 净收入
    net_income = total_income - total_expense

    return Response(
        code=200,
        message="success",
        data=TransactionSummaryResponse(
            total_income=total_income,
            total_expense=total_expense,
            total_transfer=total_transfer,
            net_income=net_income,
            transaction_count=transaction_count
        ).model_dump()
    )


@router.get("/search", response_model=Response)
async def search_transactions(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    关键词搜索交易记录

    在备注、商户名称、商品名称中搜索。
    """
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        or_(
            Transaction.remark.ilike(f"%{keyword}%"),
            Transaction.merchant_name.ilike(f"%{keyword}%"),
            Transaction.product_name.ilike(f"%{keyword}%")
        )
    )

    total = query.count()
    transactions = query.order_by(Transaction.transaction_date.desc()).limit(limit).all()

    results = []
    for t in transactions:
        results.append({
            "id": t.id,
            "type": t.type,
            "amount": float(t.amount),
            "category_name": t.category.name if t.category else None,
            "account_name": t.account.name if t.account else None,
            "transaction_date": t.transaction_date,
            "remark": t.remark,
            "merchant_name": t.merchant_name
        })

    return Response(
        code=200,
        message="success",
        data={
            "results": results,
            "total": total
        }
    )


@router.get("/{transaction_id}", response_model=Response)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取交易记录详情
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        return Response(code=404, message="交易记录不存在", data=None)

    return Response(
        code=200,
        message="success",
        data=enrich_transaction(transaction)
    )


@router.post("", response_model=Response)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建交易记录

    根据交易类型自动更新账户余额。
    - 收入: 增加账户余额
    - 支出: 减少账户余额
    - 转账: 从转出账户减少，转入账户增加
    """
    # 验证账户存在
    account = db.query(Account).filter(
        Account.id == transaction_data.account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        return Response(code=404, message="账户不存在", data=None)

    # 验证分类存在（非转账时）
    if transaction_data.type != "transfer" and transaction_data.category_id:
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id
        ).first()
        if not category:
            return Response(code=404, message="分类不存在", data=None)

    # 转账类型验证
    if transaction_data.type == "transfer":
        if not transaction_data.to_account_id:
            return Response(code=400, message="转账需要指定转入账户", data=None)

        to_account = db.query(Account).filter(
            Account.id == transaction_data.to_account_id,
            Account.user_id == current_user.id
        ).first()

        if not to_account:
            return Response(code=404, message="转入账户不存在", data=None)

        if transaction_data.to_account_id == transaction_data.account_id:
            return Response(code=400, message="不能向同一账户转账", data=None)

        # 检查余额
        if account.balance < transaction_data.amount:
            return Response(code=400, message="转出账户余额不足", data=None)

        # 更新两个账户余额
        account.balance -= transaction_data.amount
        to_account.balance += transaction_data.amount

    else:
        # 收入/支出类型更新账户余额
        if transaction_data.type == "income":
            account.balance += transaction_data.amount
        elif transaction_data.type == "expense":
            if account.balance < transaction_data.amount:
                return Response(code=400, message="账户余额不足", data=None)
            account.balance -= transaction_data.amount

    # 创建交易记录
    transaction = Transaction(
        user_id=current_user.id,
        type=transaction_data.type,
        amount=transaction_data.amount,
        category_id=transaction_data.category_id,
        account_id=transaction_data.account_id,
        to_account_id=transaction_data.to_account_id,
        transaction_date=transaction_data.transaction_date,
        remark=transaction_data.remark,
        merchant_name=transaction_data.merchant_name,
        product_name=transaction_data.product_name,
        tags=transaction_data.tags,
        location=transaction_data.location,
        images=transaction_data.images,
        source="manual"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return Response(
        code=200,
        message="创建成功",
        data=enrich_transaction(transaction)
    )


@router.put("/{transaction_id}", response_model=Response)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新交易记录

    先回退原交易的余额影响，再应用新交易的余额变化。
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        return Response(code=404, message="交易记录不存在", data=None)

    # 获取原账户
    old_account = db.query(Account).filter(
        Account.id == transaction.account_id
    ).first()

    # 1. 先回退原交易的余额影响
    if transaction.type == "income":
        old_account.balance -= transaction.amount
    elif transaction.type == "expense":
        old_account.balance += transaction.amount
    elif transaction.type == "transfer" and transaction.to_account_id:
        old_to_account = db.query(Account).filter(
            Account.id == transaction.to_account_id
        ).first()
        old_account.balance += transaction.amount
        old_to_account.balance -= transaction.amount

    # 2. 获取更新后的数据
    update_data = transaction_data.model_dump(exclude_unset=True)

    # 如果账户变更，验证新账户
    new_account_id = update_data.get("account_id", transaction.account_id)
    new_account = db.query(Account).filter(
        Account.id == new_account_id
    ).first()

    if not new_account:
        # 恢复原余额
        if transaction.type == "income":
            old_account.balance += transaction.amount
        elif transaction.type == "expense":
            old_account.balance -= transaction.amount
        return Response(code=404, message="账户不存在", data=None)

    # 3. 应用更新
    for field, value in update_data.items():
        setattr(transaction, field, value)

    # 4. 应用新交易的余额影响
    new_type = update_data.get("type", transaction.type)
    new_amount = update_data.get("amount", transaction.amount)

    if new_type == "income":
        new_account.balance += new_amount
    elif new_type == "expense":
        if new_account.balance < new_amount:
            # 恢复原余额
            if transaction.type == "income":
                old_account.balance += transaction.amount
            elif transaction.type == "expense":
                old_account.balance -= transaction.amount
            return Response(code=400, message="账户余额不足", data=None)
        new_account.balance -= new_amount
    elif new_type == "transfer":
        new_to_account_id = update_data.get("to_account_id", transaction.to_account_id)
        if not new_to_account_id:
            return Response(code=400, message="转账需要指定转入账户", data=None)

        new_to_account = db.query(Account).filter(
            Account.id == new_to_account_id
        ).first()

        if not new_to_account:
            return Response(code=404, message="转入账户不存在", data=None)

        if new_to_account_id == new_account_id:
            return Response(code=400, message="不能向同一账户转账", data=None)

        if new_account.balance < new_amount:
            return Response(code=400, message="转出账户余额不足", data=None)

        new_account.balance -= new_amount
        new_to_account.balance += new_amount

    db.commit()
    db.refresh(transaction)

    return Response(
        code=200,
        message="更新成功",
        data=enrich_transaction(transaction)
    )


@router.delete("/{transaction_id}", response_model=Response)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除交易记录

    回退交易对账户余额的影响。
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        return Response(code=404, message="交易记录不存在", data=None)

    # 获取关联账户
    account = db.query(Account).filter(
        Account.id == transaction.account_id
    ).first()

    # 回退余额
    if transaction.type == "income":
        account.balance -= transaction.amount
    elif transaction.type == "expense":
        account.balance += transaction.amount
    elif transaction.type == "transfer" and transaction.to_account_id:
        to_account = db.query(Account).filter(
            Account.id == transaction.to_account_id
        ).first()
        account.balance += transaction.amount
        to_account.balance -= transaction.amount

    db.delete(transaction)
    db.commit()

    return Response(
        code=200,
        message="删除成功",
        data=None
    )


@router.post("/{transaction_id}/mark-repeated", response_model=Response)
async def mark_transaction_repeated(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记交易为重复记录

    用于标记微信账单导入时检测到的重复交易。
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        return Response(code=404, message="交易记录不存在", data=None)

    transaction.is_repeated = True
    db.commit()
    db.refresh(transaction)

    return Response(
        code=200,
        message="标记成功",
        data=enrich_transaction(transaction)
    )
