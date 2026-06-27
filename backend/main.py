"""
智能个人财务记账系统 - FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine, Base
from app.api import api_router
from app.core.exceptions import setup_exception_handlers
from app.core.rate_limiter import RateLimitMiddleware
from app.core.metrics import MetricsMiddleware
from app.utils.logger import setup_logging, get_logger

# 初始化结构化日志（JSON 格式在生产环境启用）
setup_logging(
    debug=settings.debug,
    json_output=(settings.app_env == "production"),
)
logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""

    async def dispatch(self, request: Request, call_next):
        response: StarletteResponse = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在启动应用...")
    logger.info("环境: %s", settings.app_env)

    # 尝试创建所有表
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.warning("数据库连接失败，请检查配置: %s", e)

    yield

    logger.info("正在关闭应用...")


# 创建 FastAPI 应用
app = FastAPI(
    title="智能个人财务记账系统",
    description="一个支持微信账单导入（自动分类）、预算管理与 AI 理财建议的个人财务记账系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 安全响应头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 速率限制中间件
app.add_middleware(RateLimitMiddleware)

# 请求指标收集中间件
app.add_middleware(MetricsMiddleware)

# 设置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置异常处理器
setup_exception_handlers(app)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智能个人财务记账系统",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
