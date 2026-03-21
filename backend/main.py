"""
智能个人财务记账系统 - FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine, Base
from app.api import api_router
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建数据库表（如果不存在）
    print("[*] 正在启动应用...")
    print(f"[*] 环境: {settings.app_env}")
    print(f"[*] 调试模式: {settings.debug}")

    # 尝试创建所有表
    try:
        Base.metadata.create_all(bind=engine)
        print("[+] 数据库表初始化完成")
    except Exception as e:
        print(f"[!] 数据库连接失败，请检查配置: {e}")
        print("[!] 应用将在无数据库模式下启动（仅用于测试）")

    yield

    # 关闭时
    print("[*] 正在关闭应用...")


# 创建 FastAPI 应用
app = FastAPI(
    title="智能个人财务记账系统",
    description="一个支持微信账单导入、智能分类、预算管理的个人财务记账系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

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
