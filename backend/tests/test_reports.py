"""
分析报告 API 接口测试
"""
import pytest


class TestMonthlyReport:
    """月度报告测试"""

    def test_get_monthly_report(self, client, auth_headers, test_category, test_account):
        """获取月度报告"""
        # 创建一笔交易
        client.post("/api/transactions", headers=auth_headers, json={
            "type": "expense",
            "amount": 50,
            "category_id": test_category["id"],
            "account_id": test_account["id"],
            "transaction_date": "2026-04-10T12:00:00",
            "remark": "午餐"
        })

        response = client.get("/api/reports/monthly?year=2026&month=4", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["period"] == "2026-04"
        assert "summary" in data["data"]
        assert "total_expense" in data["data"]["summary"]
        assert "total_income" in data["data"]["summary"]
        assert "net" in data["data"]["summary"]
        assert "daily_avg_expense" in data["data"]["summary"]
        assert "top_categories" in data["data"]

    def test_get_monthly_report_missing_params(self, client, auth_headers):
        """缺少必填参数返回422"""
        response = client.get("/api/reports/monthly", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422


class TestYearlyReport:
    """年度报告测试"""

    def test_get_yearly_report(self, client, auth_headers):
        """获取年度报告"""
        response = client.get("/api/reports/yearly?year=2026", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["period"] == "2026"
        assert "summary" in data["data"]
        assert "monthly_trend" in data["data"]
        assert len(data["data"]["monthly_trend"]) == 12
        assert "top_categories" in data["data"]


class TestCategoryAnalysis:
    """分类分析测试"""

    def test_get_category_analysis(self, client, auth_headers, test_category, test_account):
        """获取分类分析"""
        # 创建交易
        client.post("/api/transactions", headers=auth_headers, json={
            "type": "expense",
            "amount": 30,
            "category_id": test_category["id"],
            "account_id": test_account["id"],
            "transaction_date": "2026-04-05T12:00:00",
            "remark": "早餐"
        })

        response = client.get(
            f"/api/reports/category/{test_category['id']}?days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "category" in data["data"]
        assert data["data"]["category"]["id"] == test_category["id"]
        assert "total_amount" in data["data"]
        assert "transaction_count" in data["data"]
        assert "avg_amount" in data["data"]
        assert "max_amount" in data["data"]
        assert "min_amount" in data["data"]

    def test_get_category_analysis_not_found(self, client, auth_headers):
        """不存在的分类返回404"""
        response = client.get("/api/reports/category/99999?days=30", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404


class TestAutoReport:
    """自动报告生成测试"""

    def test_generate_monthly_auto_report(self, client, auth_headers):
        """生成月度自动报告"""
        response = client.post("/api/reports/monthly-auto-report", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "task_id" in data["data"]
        assert data["data"]["status"] == "pending"
        assert "period" in data["data"]
