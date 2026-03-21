"""
健康检查接口
"""
from fastapi import APIRouter

from app.schemas.common import Response

router = APIRouter()


@router.get("", response_model=Response)
async def health_check():
    """健康检查"""
    return Response(
        code=200,
        message="服务运行正常",
        data={
            "status": "healthy",
            "service": "finance-backend"
        }
    )
