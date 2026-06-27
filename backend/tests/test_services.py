"""
业务逻辑单元测试
使用 Mock 隔离数据库和外部 API
"""
from unittest.mock import patch, MagicMock
from datetime import timedelta

from app.services.ai_service import AIService
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, verify_token
)


class TestPasswordHash:
    """密码加密单元测试"""

    def test_hash_and_verify_success(self):
        """密码哈希和验证成功"""
        password = "my_secure_password"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """错误密码验证失败"""
        hashed = get_password_hash("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self):
        """相同密码生成不同哈希（盐值不同）"""
        hashed1 = get_password_hash("same_password")
        hashed2 = get_password_hash("same_password")
        assert hashed1 != hashed2
        assert verify_password("same_password", hashed1) is True
        assert verify_password("same_password", hashed2) is True


class TestJWTToken:
    """JWT Token 单元测试"""

    def test_create_and_verify_token(self):
        """创建并验证 Token"""
        token = create_access_token(data={"sub": "123"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert "exp" in payload

    def test_verify_invalid_token(self):
        """无效 Token 验证返回 None"""
        result = verify_token("invalid.token.string")
        assert result is None

    def test_verify_expired_token(self):
        """过期 Token 验证返回 None"""
        token = create_access_token(
            data={"sub": "123"},
            expires_delta=timedelta(seconds=-1)
        )
        result = verify_token(token)
        assert result is None

    def test_token_contains_correct_claims(self):
        """Token 包含正确的 claims"""
        token = create_access_token(data={"sub": str(42)})
        payload = verify_token(token)
        assert payload["sub"] == "42"


class TestAIServiceRuleMatching:
    """AI 服务规则匹配单元测试（不依赖数据库和 LLM）"""

    def setup_method(self):
        self.service = AIService()

    def test_match_restaurant(self):
        """匹配餐饮分类"""
        result = self.service._match_by_rules("麦当劳", "expense")
        assert result == "餐饮"

    def test_match_coffee(self):
        """匹配咖啡到餐饮分类"""
        result = self.service._match_by_rules("瑞幸咖啡", "expense")
        assert result == "餐饮"

    def test_match_transport(self):
        """匹配交通分类"""
        result = self.service._match_by_rules("滴滴出行", "expense")
        assert result == "交通"

    def test_match_shopping(self):
        """匹配购物分类"""
        result = self.service._match_by_rules("京东商城", "expense")
        assert result == "购物"

    def test_match_medical(self):
        """匹配医疗分类"""
        result = self.service._match_by_rules("某某药店", "expense")
        assert result == "医疗"

    def test_no_match(self):
        """无法匹配返回 None"""
        result = self.service._match_by_rules("某个完全未知的商户", "expense")
        assert result is None

    def test_empty_merchant_name(self):
        """空商户名返回 None"""
        result = self.service._match_by_rules("", "expense")
        assert result is None

    def test_none_merchant_name(self):
        """None 商户名返回 None"""
        result = self.service._match_by_rules(None, "expense")
        assert result is None


class TestAIServiceAdvice:
    """AI 服务理财建议测试"""

    @patch('app.services.ai_service.OpenAI')
    def test_generate_advice_no_transactions(self, mock_openai_cls):
        """没有交易数据时返回默认建议"""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        service = AIService()
        service._client = mock_client

        db = MagicMock()
        user = MagicMock()
        user.id = 1

        # 模拟无缓存
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        # 模拟无交易
        db.query.return_value.filter.return_value.all.return_value = []

        result = service.generate_advice(db, user, months=3)

        assert result["from_cache"] is False
        assert "暂无交易数据" in result["advice"]["highlights"][0]
        assert "开始记录" in result["advice"]["suggestions"][0]
        mock_client.chat.completions.create.assert_not_called()
