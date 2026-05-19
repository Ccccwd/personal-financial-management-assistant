"""
分类管理服务
提供系统分类初始化和分类管理功能
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.account import Account


# 预设系统支出分类
SYSTEM_EXPENSE_CATEGORIES = [
    {"name": "餐饮", "icon": "🍔", "color": "#FF6B6B"},
    {"name": "交通", "icon": "🚇", "color": "#4ECDC4"},
    {"name": "购物", "icon": "🛒", "color": "#96CEB4"},
    {"name": "娱乐", "icon": "🎮", "color": "#45B7D1"},
    {"name": "医疗", "icon": "🏥", "color": "#FFEAA7"},
    {"name": "教育", "icon": "📚", "color": "#DDA0DD"},
    {"name": "住房", "icon": "🏠", "color": "#98D8C8"},
    {"name": "通讯", "icon": "📱", "color": "#F7DC6F"},
    {"name": "金融", "icon": "💰", "color": "#82E0AA"},
    {"name": "其他", "icon": "📝", "color": "#BDC3C7"},
]

# 预设系统收入分类
SYSTEM_INCOME_CATEGORIES = [
    {"name": "工资", "icon": "💰", "color": "#00B894"},
    {"name": "奖金", "icon": "🎁", "color": "#00CEC9"},
    {"name": "兼职", "icon": "💸", "color": "#0984E3"},
    {"name": "理财收益", "icon": "📈", "color": "#6C5CE7"},
    {"name": "红包", "icon": "🧧", "color": "#D63031"},
    {"name": "退款", "icon": "↩️", "color": "#E17055"},
    {"name": "其他收入", "icon": "📝", "color": "#BDC3C7"},
]


class CategoryService:
    """分类管理服务"""

    def init_user_categories(self, db: Session, user_id: int) -> List[Category]:
        """为新用户初始化系统预设分类"""
        created = []

        # 创建支出分类
        for i, cat in enumerate(SYSTEM_EXPENSE_CATEGORIES):
            existing = db.query(Category).filter(
                Category.user_id == user_id,
                Category.name == cat["name"],
                Category.type == "expense",
            ).first()
            if not existing:
                category = Category(
                    user_id=user_id,
                    name=cat["name"],
                    type="expense",
                    icon=cat["icon"],
                    color=cat["color"],
                    is_system=True,
                    sort_order=i,
                )
                db.add(category)
                created.append(category)

        # 创建收入分类
        for i, cat in enumerate(SYSTEM_INCOME_CATEGORIES):
            existing = db.query(Category).filter(
                Category.user_id == user_id,
                Category.name == cat["name"],
                Category.type == "income",
            ).first()
            if not existing:
                category = Category(
                    user_id=user_id,
                    name=cat["name"],
                    type="income",
                    icon=cat["icon"],
                    color=cat["color"],
                    is_system=True,
                    sort_order=i,
                )
                db.add(category)
                created.append(category)

        db.commit()
        return created

    def init_default_account(self, db: Session, user_id: int) -> Optional[Account]:
        """为新用户创建默认账户"""
        existing = db.query(Account).filter(
            Account.user_id == user_id,
            Account.is_default,
        ).first()
        if existing:
            return existing

        account = Account(
            user_id=user_id,
            name="默认账户",
            type="cash",
            initial_balance=0,
            balance=0,
            is_default=True,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    def init_user_defaults(self, db: Session, user_id: int):
        """为新用户初始化所有默认数据（分类 + 账户）"""
        self.init_user_categories(db, user_id)
        self.init_default_account(db, user_id)
