"""
余额历史 API 接口测试
"""
import pytest


class TestBalanceHistory:
    """余额历史测试"""

    def test_get_all_balance_history(self, client, auth_headers, test_account):
        """获取所有账户余额历史"""
        response = client.get("/api/balance-history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert "total" in data["data"]

    def test_get_balance_history_with_filter(self, client, auth_headers, test_account, test_category):
        """按类型过滤余额历史"""
        # 创建交易
        client.post("/api/transactions", headers=auth_headers, json={
            "type": "expense",
            "amount": 20,
            "category_id": test_category["id"],
            "account_id": test_account["id"],
            "transaction_date": "2026-04-10T12:00:00",
            "remark": "测试"
        })

        response = client.get("/api/balance-history?change_type=expense", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        for item in data["data"]["items"]:
            assert item["type"] == "expense"

    def test_get_account_balance_history(self, client, auth_headers, test_account):
        """获取指定账户余额历史"""
        account_id = test_account["id"]
        response = client.get(f"/api/accounts/{account_id}/balance-history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_balance_history_pagination(self, client, auth_headers, test_account):
        """余额历史分页"""
        response = client.get("/api/balance-history?limit=5&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["limit"] == 5
        assert data["data"]["offset"] == 0
