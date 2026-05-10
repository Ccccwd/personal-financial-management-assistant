"""
API 速率限制中间件
基于 IP 地址的简单速率限制，防止暴力破解
"""
import os
import time
from collections import defaultdict
from typing import Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiter:
    """滑动窗口速率限制器"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """检查请求是否被允许"""
        now = time.time()
        cutoff = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True


# 登录接口限制：5次/分钟
login_limiter = RateLimiter(max_requests=5, window_seconds=60)

# 全局API限制：60次/分钟
global_limiter = RateLimiter(max_requests=60, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    # 需要严格限制的路径（登录、注册、密码重置）
    STRICT_PATHS = ("/api/auth/login", "/api/auth/register", "/api/auth/password-reset-request")

    async def dispatch(self, request: Request, call_next):
        # 测试环境跳过速率限制
        if os.getenv("APP_ENV", "development") == "testing":
            return await call_next(request)

        # 只限制 API 请求
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # 登录等敏感接口使用严格限制
        if request.url.path in self.STRICT_PATHS:
            if not login_limiter.is_allowed(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None}
                )

        # 全局速率限制
        if not global_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None}
            )

        return await call_next(request)
