"""
AI 智能服务 API 接口测试
使用 Mock 隔离 LLM 调用
"""
from unittest.mock import patch


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
