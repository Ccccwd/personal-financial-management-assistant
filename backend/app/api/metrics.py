"""
指标查询接口
提供请求计数、响应时间、错误率等运行指标
"""
from fastapi import APIRouter

from app.core.metrics import metrics
from app.schemas.common import Response

router = APIRouter()


@router.get("", response_model=Response)
async def get_metrics():
    """
    获取应用运行指标

    返回请求总数、错误率、平均响应时间、Top 接口等指标。
    """
    return Response(
        code=200,
        message="指标获取成功",
        data=metrics.get_summary(),
    )
