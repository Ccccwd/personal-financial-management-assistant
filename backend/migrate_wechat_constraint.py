"""
迁移脚本：将 wechat_transaction_id 的唯一约束从 (user_id, wechat_transaction_id)
改为 (user_id, account_id, wechat_transaction_id)

运行方式：
    cd backend
    uv run python migrate_wechat_constraint.py
"""
from app.config.database import engine


def _drop_old_index(conn, index_name: str) -> None:
    """删除可能存在的旧唯一索引（不同环境索引名可能不同）。"""
    try:
        conn.execute(
            __import__("sqlalchemy").text(
                f"ALTER TABLE transactions DROP INDEX {index_name}"
            )
        )
        conn.commit()
        print(f"✅ 已删除旧约束 {index_name}")
    except Exception as e:
        err = str(e).lower()
        if "check that" in err or "exist" in err or "can't drop" in err:
            print(f"⚠️  旧约束 {index_name} 不存在，跳过: {e}")
        else:
            raise


def migrate():
    with engine.connect() as conn:
        # 1. 删除所有历史版本的唯一约束
        for old_index in ("wechat_transaction_id", "uq_user_wechat_txn", "uq_user_account_wechat_txn"):
            _drop_old_index(conn, old_index)

        # 2. 添加新的唯一约束
        try:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE transactions ADD CONSTRAINT uq_user_account_wechat_txn "
                    "UNIQUE (user_id, account_id, wechat_transaction_id)"
                )
            )
            conn.commit()
            print("✅ 已添加新约束 uq_user_account_wechat_txn (user_id, account_id, wechat_transaction_id)")
        except Exception as e:
            if "duplicate" in str(e).lower() or "exist" in str(e).lower():
                print(f"⚠️  新约束已存在，跳过: {e}")
            else:
                raise

    print("\n迁移完成！")


if __name__ == "__main__":
    migrate()
