"""
Redis 配置模块
"""
import redis
from .settings import settings


def get_redis_client() -> redis.Redis:
    """获取 Redis 客户端"""
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )


# Redis 客户端实例（延迟初始化）
_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """获取 Redis 客户端单例"""
    global _redis_client
    if _redis_client is None:
        _redis_client = get_redis_client()
    return _redis_client
