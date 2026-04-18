"""
全局配置模块
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/finance_db"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # JWT 配置
    secret_key: str = "dev_secret_key_please_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI 大模型配置
    ai_api_key: str = ""
    ai_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    ai_model: str = "glm-5.1"

    # 应用配置
    app_env: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
