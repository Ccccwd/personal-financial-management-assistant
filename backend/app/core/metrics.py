"""
请求指标收集中间件
收集请求计数、响应时间、错误率等基础指标
"""
import time
from collections import defaultdict
from typing import Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from app.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """指标收集器（进程内存储）"""

    def __init__(self):
        self._request_count: Dict[str, int] = defaultdict(int)
        self._error_count: Dict[str, int] = defaultdict(int)
        self._response_times: Dict[str, List[float]] = defaultdict(list)
        self._total_requests: int = 0
        self._total_errors: int = 0

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        """
        记录一次请求

        Args:
            method: HTTP 方法
            path: 请求路径
            status_code: 响应状态码
            duration: 响应时间（秒）
        """
        key = f"{method} {path}"
        self._request_count[key] += 1
        self._total_requests += 1

        # 记录响应时间（保留最近 1000 条）
        times = self._response_times[key]
        times.append(duration)
        if len(times) > 1000:
            self._response_times[key] = times[-1000:]

        # 错误计数（4xx/5xx）
        if status_code >= 400:
            self._error_count[key] += 1
            self._total_errors += 1

    def get_summary(self) -> dict:
        """获取指标摘要"""
        total = self._total_requests
        errors = self._total_errors

        # 计算全局平均响应时间
        all_times = []
        for times in self._response_times.values():
            all_times.extend(times[-100:])

        avg_response_time = round(sum(all_times) / len(all_times), 4) if all_times else 0

        # 按路径取 Top 10 请求量
        top_endpoints = sorted(
            self._request_count.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total_requests": total,
            "total_errors": errors,
            "error_rate": round(errors / total * 100, 2) if total > 0 else 0,
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "top_endpoints": [
                {"endpoint": ep, "count": count}
                for ep, count in top_endpoints
            ],
        }


# 全局指标收集器实例
metrics = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """请求指标收集中间件"""

    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和指标端点自身，避免干扰
        if request.url.path in ("/api/health", "/api/metrics", "/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        start_time = time.time()
        response: StarletteResponse = await call_next(request)
        duration = time.time() - start_time

        # 记录指标
        metrics.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        # 慢请求告警（超过 2 秒）
        if duration > 2.0:
            logger.warning(
                "慢请求: %s %s (%.2fs, %d)",
                request.method, request.url.path, duration, response.status_code,
            )

        # 添加响应时间头
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        return response
