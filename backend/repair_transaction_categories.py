"""
修复交易记录中错误的跨用户分类，并按规则重新分类。

运行方式：
    cd backend
    uv run python repair_transaction_categories.py
"""
from sqlalchemy import text

from app.config.database import SessionLocal
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.ai_service import AIService


def repair_invalid_category_links(db) -> int:
    """清除 category_id 指向其他用户分类的记录。"""
    result = db.execute(
        text("""
            UPDATE transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            SET t.category_id = NULL, t.ai_classified = 0
            WHERE t.category_id IS NOT NULL
              AND (c.id IS NULL OR c.user_id != t.user_id)
        """)
    )
    db.commit()
    return result.rowcount or 0


def reclassify_by_rules(db, user_id: int | None = None) -> int:
    """对无分类交易按规则重新分类。"""
    ai_service = AIService()
    query = db.query(Transaction).filter(Transaction.category_id.is_(None))
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    transactions = query.all()

    updated = 0
    for txn in transactions:
        if txn.type == "transfer":
            continue
        search_text = f"{txn.merchant_name or ''} {txn.remark or ''}".strip()
        matched_name = ai_service._match_by_rules(search_text, txn.type)
        category = None
        if matched_name:
            category = ai_service._find_category_by_name(
                db, txn.user_id, matched_name, txn.type
            )
        if category is None:
            fallback_id = ai_service._get_fallback_category_id(db, txn.user_id, txn.type)
            if fallback_id:
                category = db.query(Category).filter(Category.id == fallback_id).first()
        if category:
            txn.category_id = category.id
            txn.ai_classified = matched_name is not None
            updated += 1

    if updated:
        db.commit()
    return updated


def main():
    db = SessionLocal()
    try:
        cleared = repair_invalid_category_links(db)
        print(f"✅ 已清除 {cleared} 条跨用户错误分类")

        reclassified = reclassify_by_rules(db)
        print(f"✅ 已按规则重新分类 {reclassified} 条交易")
    finally:
        db.close()

    print("\n修复完成！")


if __name__ == "__main__":
    main()
