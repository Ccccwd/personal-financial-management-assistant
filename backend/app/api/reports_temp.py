"""
分类管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryListResponse
)
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=Response)
async def get_categories(
    type: Optional[str] = Query(None, description="分类类型: income/expense"),
    include_system: bool = Query(True, description="是否包含系统分类"),
    parent_id: Optional[int] = Query(None, description="父分类ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类列表

    - **type**: 过滤分类类型 (income/expense)
    - **include_system**: 是否包含系统预设分类
    - **parent_id**: 过滤指定父分类下的子分类
    """
    query = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.is_system)
    )

    if type:
        query = query.filter(Category.type == type)

    if not include_system:
        query = query.filter(not Category.is_system)

    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)

    categories = query.order_by(Category.sort_order, Category.id).all()

    return Response(
        code=200,
        message="success",
        data=CategoryListResponse(
            categories=[CategoryResponse.model_validate(c) for c in categories],
            total=len(categories)
        ).model_dump()
    )


@router.get("/tree", response_model=Response)
async def get_category_tree(
    type: Optional[str] = Query(None, description="分类类型: income/expense"),
    include_system: bool = Query(True, description="是否包含系统分类"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类树结构

    返回带有 children 字段的树形结构，便于前端展示层级分类。
    """
    query = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.is_system)
    )

    if type:
        query = query.filter(Category.type == type)

    if not include_system:
        query = query.filter(not Category.is_system)

    all_categories = query.order_by(Category.sort_order, Category.id).all()

    # 构建树形结构
    def build_tree(categories: List[Category], parent_id: Optional[int] = None) -> List[dict]:
        tree = []
        for cat in categories:
            if cat.parent_id == parent_id:
                cat_dict = CategoryResponse.model_validate(cat).model_dump()
                children = build_tree(categories, cat.id)
                if children:
                    cat_dict["children"] = children
                else:
                    cat_dict["children"] = []
                tree.append(cat_dict)
        return tree

    tree = build_tree(all_categories)

    return Response(
        code=200,
        message="success",
        data=tree
    )


@router.get("/stats", response_model=Response)
async def get_categories_with_stats(
    type: Optional[str] = Query(None, description="分类类型: income/expense"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取带使用统计的分类列表

    返回每个分类的交易次数和总金额统计。
    """
    query = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.is_system)
    )

    if type:
        query = query.filter(Category.type == type)

    categories = query.order_by(Category.sort_order, Category.id).limit(limit).all()

    # 查询每个分类的交易统计
    result = []
    for cat in categories:
        # 统计该分类下的交易数量
        transaction_count = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == cat.id
        ).count()

        # 统计该分类下的总金额
        total_amount = db.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == cat.id
        ).scalar() or 0

        cat_dict = CategoryResponse.model_validate(cat).model_dump()
        cat_dict["transaction_count"] = transaction_count
        cat_dict["total_amount"] = float(total_amount)
        result.append(cat_dict)

    return Response(
        code=200,
        message="success",
        data={
            "categories": result,
            "total": len(result)
        }
    )


@router.get("/{category_id}", response_model=Response)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类详情
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        (Category.user_id == current_user.id) | (Category.is_system)
    ).first()

    if not category:
        return Response(code=404, message="分类不存在", data=None)

    return Response(
        code=200,
        message="success",
        data=CategoryResponse.model_validate(category).model_dump()
    )


@router.post("", response_model=Response)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建分类

    用户只能创建自定义分类，系统分类不可创建。
    """
    # 检查同名分类是否已存在
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_data.name,
        Category.type == category_data.type
    ).first()

    if existing:
        return Response(code=400, message="该分类名称已存在", data=None)

    # 验证父分类是否存在
    if category_data.parent_id:
        parent = db.query(Category).filter(
            Category.id == category_data.parent_id,
            (Category.user_id == current_user.id) | (Category.is_system)
        ).first()
        if not parent:
            return Response(code=400, message="父分类不存在", data=None)

    category = Category(
        user_id=current_user.id,
        name=category_data.name,
        type=category_data.type,
        icon=category_data.icon,
        color=category_data.color,
        parent_id=category_data.parent_id,
        sort_order=category_data.sort_order,
        is_system=False
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return Response(
        code=200,
        message="创建成功",
        data=CategoryResponse.model_validate(category).model_dump()
    )


@router.put("/{category_id}", response_model=Response)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新分类

    系统分类不可修改。支持部分字段更新。
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        return Response(code=404, message="分类不存在或无权限修改", data=None)

    if category.is_system:
        return Response(code=400, message="系统分类不可修改", data=None)

    # 更新字段
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return Response(
        code=200,
        message="更新成功",
        data=CategoryResponse.model_validate(category).model_dump()
    )


@router.delete("/{category_id}", response_model=Response)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除分类

    系统分类不可删除。有子分类的分类不可删除。
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        return Response(code=404, message="分类不存在或无权限删除", data=None)

    if category.is_system:
        return Response(code=400, message="系统分类不可删除", data=None)

    # 检查是否有子分类
    children_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if children_count > 0:
        return Response(code=400, message="该分类下有子分类，无法删除", data=None)

    # 检查是否有关联的交易记录
    transactions_count = db.query(Transaction).filter(Transaction.category_id == category_id).count()
    if transactions_count > 0:
        return Response(code=400, message="该分类下有交易记录，无法删除", data=None)

    db.delete(category)
    db.commit()

    return Response(
        code=200,
        message="删除成功",
        data=None
    )
