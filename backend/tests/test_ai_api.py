"""
AI 智能服务 API 接口测试
使用 Mock 隔离 LLM 调用
"""
import pytest
from unittest.mock import patch, MagicMock
import json


class TestAIClassify:
    """智能分类测试"""

    @patch('app.services.ai_service.AIService.classify_items')
    def test_classify_success(self, mock_classify, client, auth_headers):
        """智能分类成功"""
        mock_classify.return_value = {
            "results": [
                {"index": 0, "merchant_name": "瑞幸咖啡", "category_id": 1, "category_name": "餐饮", "confidence": 0.9, "matched_by": "rule"},
                {"index": 1, "merchant_name": "未知商店", "category_id": 5, "category_name": "其他", "confidence": 0.7, "matched_by": "llm"}
            ],
            "total": 2,
            "llm_called_count": 1,
            "rule_matched_count": 1
        }

        response = client.post("/api/ai/classify", headers=auth_headers, json={
            "items": [
                {"merchant_name": "瑞幸咖啡", "amount": 15.9, "transaction_type": "expense"},
                {"merchant_name": "未知商店", "amount": 100.0, "transaction_type": "expense"}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total"] == 2
        assert data["data"]["rule_matched_count"] == 1

    def test_classify_unauthorized(self, client):
        """未认证返回401"""
        response = client.post("/api/ai/classify", json={
            "items": [{"merchant_name": "test", "amount": 10, "transaction_type": "expense"}]
        })
        assert response.status_code == 401


class TestAIReclassify:
    """重新分类测试"""

    @patch('app.services.ai_service.AIService.reclassify_transaction')
    def test_reclassify_dry_run(self, mock_reclassify, client, auth_headers):
        """预览重新分类"""
        mock_reclassify.return_value = {
            "transaction_id": 1,
            "category_id": 2,
            "category_name": "交通",
            "confidence": 0.85,
            "matched_by": "llm"
        }

        response = client.post("/api/ai/reclassify/1?dry_run=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["matched_by"] == "llm"

    @patch('app.services.ai_service.AIService.reclassify_transaction')
    def test_reclassify_not_found(self, mock_reclassify, client, auth_headers):
        """交易不存在返回404"""
        mock_reclassify.return_value = None

        response = client.post("/api/ai/reclassify/99999", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404


class TestAIAdvice:
    """理财建议测试"""

    @patch('app.services.ai_service.AIService.generate_advice')
    def test_get_advice_success(self, mock_advice, client, auth_headers):
        """获取理财建议成功"""
        from datetime import datetime
        now = datetime.now()
        mock_advice.return_value = {
            "generated_at": now,
            "from_cache": False,
            "analysis_period": {"start": now, "end": now},
            "advice": {
                "highlights": ["餐饮支出控制良好"],
                "warnings": ["娱乐消费偏高"],
                "suggestions": ["建议减少娱乐支出"],
                "next_month_budget": {"total": 3000},
                "full_report": "本月消费总结..."
            }
        }

        response = client.get("/api/ai/advice?months=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "advice" in data["data"]
        assert "highlights" in data["data"]["advice"]


class TestAIAdviceHistory:
    """建议历史测试"""

    def test_get_advice_history_empty(self, client, auth_headers):
        """无历史记录时返回空列表"""
        response = client.get("/api/ai/advice/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["items"] == []
        assert data["data"]["total"] == 0

    def test_get_advice_history_not_found(self, client, auth_headers):
        """不存在的记录返回404"""
        response = client.get("/api/ai/advice/history/99999", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404


class TestAIUsage:
    """用量统计测试"""

    def test_get_usage_stats(self, client, auth_headers):
        """获取用量统计"""
        response = client.get("/api/ai/usage?year=2026&month=4", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "month" in data["data"]
        assert "classify_calls" in data["data"]
        assert "advice_calls" in data["data"]
        assert "total_tokens_used" in data["data"]

    def test_get_usage_stats_default_params(self, client, auth_headers):
        """默认参数获取当前月统计"""
        response = client.get("/api/ai/usage", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
