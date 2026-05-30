"""
健康检查接口
提供应用运行状态、数据库连接、Redis 连接等检查
"""
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.config.database import SessionLocal
from app.config.redis import get_redis_client
from app.schemas.common import Response

router = APIRouter()

# 应用启动时间（模块加载时记录）
_start_time = datetime.now(tz=timezone.utc)


def _calculate_uptime() -> str:
    """计算运行时长"""
    delta = datetime.now(tz=timezone.utc) - _start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def _check_database() -> dict:
    """检查数据库连接"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "type": "MySQL"}
    except Exception as e:
        return {"status": "unhealthy", "type": "MySQL", "error": str(e)}


def _check_redis() -> dict:
    """检查 Redis 连接"""
    try:
        redis = get_redis_client()
        redis.ping()
        return {"status": "healthy", "type": "Redis"}
    except Exception as e:
        return {"status": "unhealthy", "type": "Redis", "error": str(e)}


@router.get("", response_model=Response)
async def health_check():
    """
    健康检查端点

    返回应用状态、版本、运行时长、数据库和 Redis 连接状态。
    """
    db_status = _check_database()
    redis_status = _check_redis()

    is_healthy = (
        db_status["status"] == "healthy"
        and redis_status["status"] == "healthy"
    )

    return Response(
        code=200,
        message="服务运行正常" if is_healthy else "部分服务异常",
        data={
            "status": "healthy" if is_healthy else "degraded",
            "service": "finance-backend",
            "version": "1.0.0",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "uptime": _calculate_uptime(),
            "checks": {
                "database": db_status,
                "redis": redis_status,
            },
        },
    )
