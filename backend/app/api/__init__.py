from fastapi import APIRouter
from . import auth, health, categories, accounts, transactions, budgets, statistics, reminders, reports, balance_history, ai

api_router = APIRouter()

# 注册路由
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(categories.router, prefix="/categories", tags=["分类管理"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["账户管理"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["交易记录"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["预算管理"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["提醒管理"])
api_router.include_router(reports.router, prefix="/reports", tags=["分析报告"])
api_router.include_router(balance_history.router, prefix="/balance-history", tags=["余额历史"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI智能服务"])
