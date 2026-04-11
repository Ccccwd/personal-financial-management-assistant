"""
账户管理接口测试
"""
import pytest
from decimal import Decimal


class TestCreateAccount:
    """创建账户测试"""

    def test_create_account(self, client, auth_headers):
        """创建账户，余额=初始余额"""
        response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "现金账户",
            "type": "cash",
            "initial_balance": "1000.00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "创建成功"
        assert data["data"]["name"] == "现金账户"
        assert data["data"]["balance"] == "1000.00"
        assert data["data"]["initial_balance"] == "1000.00"
        assert data["data"]["is_default"] is False

    def test_create_account_default(self, client, auth_headers):
        """设置默认账户时取消其他默认"""
        # 创建第一个默认账户
        client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户1",
            "type": "cash",
            "initial_balance": "500.00",
            "is_default": True
        })

        # 创建第二个默认账户
        response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户2",
            "type": "bank",
            "initial_balance": "2000.00",
            "is_default": True
        })
        assert response.status_code == 200

        # 获取账户列表，检查只有账户2是默认账户
        list_response = client.get("/api/accounts", headers=auth_headers)
        accounts = list_response.json()["data"]["accounts"]

        default_accounts = [a for a in accounts if a["is_default"] is True]
        assert len(default_accounts) == 1
        assert default_accounts[0]["name"] == "账户2"

    def test_create_account_duplicate_name(self, client, auth_headers):
        """创建同名账户返回400"""
        client.post("/api/accounts", headers=auth_headers, json={
            "name": "现金账户",
            "type": "cash"
        })

        response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "现金账户",
            "type": "bank"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "已存在" in data["message"]

    def test_create_account_unauthorized(self, client):
        """未认证时创建账户返回401"""
        response = client.post("/api/accounts", json={
            "name": "测试账户"
        })
        assert response.status_code == 401


class TestGetAccounts:
    """获取账户列表测试"""

    def test_get_accounts_list(self, client, auth_headers, test_account):
        """获取账户列表"""
        response = client.get("/api/accounts", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["accounts"]) > 0
        assert data["data"]["total"] > 0

    def test_get_accounts_filter_by_type(self, client, auth_headers, test_account):
        """按类型过滤账户"""
        response = client.get("/api/accounts?type=cash", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for account in data["data"]["accounts"]:
            assert account["type"] == "cash"

    def test_get_accounts_filter_enabled(self, client, auth_headers):
        """过滤启用状态的账户"""
        response = client.get("/api/accounts?is_enabled=true", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for account in data["data"]["accounts"]:
            assert account["is_enabled"] is True


class TestAccountSummary:
    """账户统计摘要测试"""

    def test_get_account_summary(self, client, auth_headers, test_account):
        """获取统计摘要"""
        response = client.get("/api/accounts/summary", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert "total_balance" in data["data"]
        assert "total_accounts" in data["data"]
        assert "account_distribution" in data["data"]
        # 余额返回为字符串格式，使用数值比较
        assert float(data["data"]["total_balance"]) == 1000.0

    def test_get_account_summary_multiple_accounts(self, client, auth_headers):
        """多个账户的统计摘要"""
        # 创建多个账户
        client.post("/api/accounts", headers=auth_headers, json={
            "name": "现金",
            "type": "cash",
            "initial_balance": "500.00"
        })
        client.post("/api/accounts", headers=auth_headers, json={
            "name": "银行卡",
            "type": "bank",
            "initial_balance": "2000.00"
        })

        response = client.get("/api/accounts/summary", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["total_accounts"] == 2
        assert float(data["data"]["total_balance"]) == 2500.00


class TestDefaultAccount:
    """默认账户测试"""

    def test_get_default_account(self, client, auth_headers, test_account):
        """获取默认账户"""
        response = client.get("/api/accounts/default", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["is_default"] is True

    def test_get_default_account_no_default(self, client, auth_headers):
        """没有设置默认账户时返回第一个启用的账户"""
        # 创建非默认账户
        client.post("/api/accounts", headers=auth_headers, json={
            "name": "普通账户",
            "type": "cash",
            "initial_balance": "100.00",
            "is_default": False
        })

        response = client.get("/api/accounts/default", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "普通账户"

    def test_get_default_account_no_accounts(self, client, auth_headers):
        """没有账户时返回404"""
        response = client.get("/api/accounts/default", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestTransfer:
    """转账测试"""

    def test_transfer(self, client, auth_headers):
        """两个账户间转账"""
        # 创建两个账户
        from_account_response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户A",
            "type": "cash",
            "initial_balance": "1000.00"
        })
        from_account_id = from_account_response.json()["data"]["id"]

        to_account_response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户B",
            "type": "bank",
            "initial_balance": "500.00"
        })
        to_account_id = to_account_response.json()["data"]["id"]

        # 执行转账
        response = client.post("/api/accounts/transfer", headers=auth_headers, json={
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": "200.00",
            "remark": "转账测试"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "转账成功"
        assert data["data"]["from_account_balance"] == "800.00"
        assert data["data"]["to_account_balance"] == "700.00"

    def test_transfer_insufficient_balance(self, client, auth_headers):
        """余额不足时返回400"""
        # 创建两个账户
        from_account_response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户A",
            "type": "cash",
            "initial_balance": "100.00"
        })
        from_account_id = from_account_response.json()["data"]["id"]

        to_account_response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "账户B",
            "type": "bank",
            "initial_balance": "500.00"
        })
        to_account_id = to_account_response.json()["data"]["id"]

        # 尝试转账超过余额
        response = client.post("/api/accounts/transfer", headers=auth_headers, json={
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": "200.00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "余额不足" in data["message"]

    def test_transfer_same_account(self, client, auth_headers, test_account):
        """向同一账户转账返回400"""
        account_id = test_account["id"]

        response = client.post("/api/accounts/transfer", headers=auth_headers, json={
            "from_account_id": account_id,
            "to_account_id": account_id,
            "amount": "100.00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "同一账户" in data["message"]

    def test_transfer_account_not_found(self, client, auth_headers, test_account):
        """转出/转入账户不存在返回404"""
        response = client.post("/api/accounts/transfer", headers=auth_headers, json={
            "from_account_id": test_account["id"],
            "to_account_id": 99999,
            "amount": "100.00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestDeleteAccount:
    """删除账户测试"""

    def test_delete_account(self, client, auth_headers):
        """删除账户"""
        account_response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "临时账户",
            "type": "cash",
            "initial_balance": "100.00"
        })
        account_id = account_response.json()["data"]["id"]

        response = client.delete(f"/api/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "删除成功"

    def test_delete_account_with_transactions(self, client, auth_headers, test_account, test_category):
        """有交易记录时不可删除"""
        # 需要先创建交易记录，但由于交易API可能未完成，暂时跳过
        # 这个测试可以在交易API完成后补充
        pass

    def test_delete_account_not_found(self, client, auth_headers):
        """删除不存在的账户返回404"""
        response = client.delete("/api/accounts/99999", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestUpdateAccount:
    """更新账户测试"""

    def test_update_account(self, client, auth_headers, test_account):
        """更新账户信息"""
        account_id = test_account["id"]

        response = client.put(f"/api/accounts/{account_id}", headers=auth_headers, json={
            "name": "更新后的账户名",
            "color": "#00FF00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "更新后的账户名"
        assert data["data"]["color"] == "#00FF00"

    def test_update_account_not_found(self, client, auth_headers):
        """更新不存在的账户返回404"""
        response = client.put("/api/accounts/99999", headers=auth_headers, json={
            "name": "测试"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestAdjustBalance:
    """余额调整测试"""

    def test_adjust_balance(self, client, auth_headers, test_account):
        """调整余额"""
        account_id = test_account["id"]
        old_balance = float(test_account["balance"])

        response = client.post(f"/api/accounts/{account_id}/adjust-balance", headers=auth_headers, json={
            "new_balance": "1500.00",
            "remark": "余额校正"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        # API 返回的是浮点数
        assert data["data"]["new_balance"] == 1500.0
        assert data["data"]["old_balance"] == old_balance
        assert data["data"]["difference"] == 500.0

    def test_adjust_balance_decrease(self, client, auth_headers, test_account):
        """调减余额"""
        account_id = test_account["id"]

        response = client.post(f"/api/accounts/{account_id}/adjust-balance", headers=auth_headers, json={
            "new_balance": "500.00"
        })
        assert response.status_code == 200

        data = response.json()
        # API 返回的是浮点数
        assert data["data"]["new_balance"] == 500.0
        assert data["data"]["difference"] == -500.0

    def test_adjust_balance_not_found(self, client, auth_headers):
        """调整不存在的账户余额返回404"""
        response = client.post("/api/accounts/99999/adjust-balance", headers=auth_headers, json={
            "new_balance": "1000.00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestAccountDetail:
    """账户详情测试"""

    def test_get_account_detail(self, client, auth_headers, test_account):
        """获取账户详情"""
        account_id = test_account["id"]

        response = client.get(f"/api/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == account_id
        assert "income_total" in data["data"]
        assert "expense_total" in data["data"]

    def test_get_account_detail_not_found(self, client, auth_headers):
        """获取不存在的账户返回404"""
        response = client.get("/api/accounts/99999", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404
