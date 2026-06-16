"""预算建议归一化单元测试"""
from app.services.ai_service import normalize_budget_suggestion


class TestNormalizeBudgetSuggestion:
    """测试 normalize_budget_suggestion 函数"""

    def test_normalize_chinese_keys(self):
        """兼容 LLM 返回的中文键名"""
        raw = {
            "总预算": 270,
            "各分类预算": {
                "餐饮": 100,
                "其他": 50,
            },
        }
        result = normalize_budget_suggestion(raw)
        assert result is not None
        assert result["total"] == 270
        assert len(result["breakdown"]) == 2
        assert result["breakdown"][0]["category"] == "餐饮"
        assert result["breakdown"][0]["suggested_amount"] == 100

    def test_normalize_english_keys(self):
        """兼容 API 约定的英文键名"""
        raw = {
            "total": 3500,
            "breakdown": [
                {"category": "餐饮", "suggested_amount": 900},
                {"category": "交通", "suggested_amount": 300},
            ],
        }
        result = normalize_budget_suggestion(raw)
        assert result is not None
        assert result["total"] == 3500
        assert len(result["breakdown"]) == 2

    def test_compute_total_from_breakdown(self):
        """缺少 total 时从 breakdown 求和"""
        raw = {
            "各分类预算": {"餐饮": 100, "交通": 50},
        }
        result = normalize_budget_suggestion(raw)
        assert result is not None
        assert result["total"] == 150

    def test_returns_none_for_empty(self):
        """空数据返回 None"""
        assert normalize_budget_suggestion(None) is None
        assert normalize_budget_suggestion({}) is None
