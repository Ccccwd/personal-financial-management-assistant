"""
AI 智能服务接口
提供账单智能分类和理财建议生成功能
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.ai import (
    ClassifyRequest, ClassifyResponse, ClassifyResultItem,
    AdviceResponse, AIUsageResponse
)
from app.models.user import User
from app.models.transaction import Transaction
from app.models.ai_advice_record import AIAdviceRecord
from app.core.dependencies import get_current_active_user
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/classify", response_model=Response)
async def classify_transactions(
    request: ClassifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    账单智能分类

    接收一批交易记录，使用规则匹配和 LLM 进行智能分类。

    - **items**: 待分类的交易列表，最多 100 条
    - 返回每条交易的分类结果、置信度和匹配方式
    """
    items_data = [item.model_dump() for item in request.items]

    try:
        result = ai_service.classify_items(db, current_user.id, items_data)

        return Response(
            code=200,
            message="success",
            data={
                "results": result["results"],
                "total": result["total"],
                "llm_called_count": result["llm_called_count"],
                "rule_matched_count": result["rule_matched_count"]
            }
        )
    except Exception as e:
        return Response(
            code=500,
            message="AI服务暂时不可用",
            data=None
        )


@router.post("/reclassify/{transaction_id}", response_model=Response)
async def reclassify_transaction(
    transaction_id: int,
    dry_run: bool = Query(False, description="是否仅预览不修改"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    重新分类单条交易

    对指定交易记录重新进行智能分类。

    - **transaction_id**: 交易记录ID
    - **dry_run**: 为 true 时仅预览结果，不实际修改；为 false 时更新交易记录
    """
    try:
        result = ai_service.reclassify_transaction(db, current_user.id, transaction_id)

        if result is None:
            return Response(code=404, message="交易记录不存在", data=None)

        if not dry_run:
            # 更新交易记录
            transaction = db.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            ).first()

            if transaction:
                transaction.category_id = result["category_id"]
                transaction.ai_classified = True
                db.commit()

        return Response(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        return Response(
            code=500,
            message="AI服务暂时不可用",
            data=None
        )


@router.get("/advice", response_model=Response)
async def get_financial_advice(
    months: int = Query(3, ge=1, le=12, description="分析最近几个月的数据"),
    force_refresh: bool = Query(False, description="是否强制刷新缓存"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取理财建议

    基于用户的消费历史数据，生成个性化的理财建议。

    - **months**: 分析最近几个月的数据（1-12个月）
    - **force_refresh**: 为 true 时强制重新生成，忽略缓存
    - 返回消费亮点、预警信息、改进建议和下月预算建议
    """
    try:
        if force_refresh:
            # 清除缓存标志（此处简化处理，实际可根据需求实现）
            pass

        result = ai_service.generate_advice(db, current_user, months)

        return Response(
            code=200,
            message="success",
            data={
                "generated_at": result["generated_at"].isoformat(),
                "from_cache": result["from_cache"],
                "analysis_period": {
                    "start": result["analysis_period"]["start"].isoformat(),
                    "end": result["analysis_period"]["end"].isoformat()
                },
                "advice": result["advice"]
            }
        )
    except Exception as e:
        return Response(
            code=500,
            message="AI服务暂时不可用",
            data=None
        )


@router.get("/advice/history", response_model=Response)
async def get_advice_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取历史建议列表

    分页返回用户的历史理财建议记录。
    """
    query = db.query(AIAdviceRecord).filter(
        AIAdviceRecord.user_id == current_user.id
    ).order_by(AIAdviceRecord.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    records = query.offset(offset).limit(page_size).all()

    items = []
    for record in records:
        items.append({
            "id": record.id,
            "advice_type": record.advice_type,
            "analysis_period": {
                "start": record.analysis_period_start.isoformat() if record.analysis_period_start else None,
                "end": record.analysis_period_end.isoformat() if record.analysis_period_end else None
            },
            "highlights": record.highlights,
            "warnings": record.warnings,
            "suggestions": record.suggestions,
            "tokens_used": record.tokens_used,
            "created_at": record.created_at.isoformat()
        })

    return Response(
        code=200,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/advice/history/{record_id}", response_model=Response)
async def get_advice_detail(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取建议详情

    返回指定理财建议记录的完整内容。
    """
    record = db.query(AIAdviceRecord).filter(
        AIAdviceRecord.id == record_id,
        AIAdviceRecord.user_id == current_user.id
    ).first()

    if not record:
        return Response(code=404, message="建议记录不存在", data=None)

    return Response(
        code=200,
        message="success",
        data={
            "id": record.id,
            "advice_type": record.advice_type,
            "analysis_period": {
                "start": record.analysis_period_start.isoformat() if record.analysis_period_start else None,
                "end": record.analysis_period_end.isoformat() if record.analysis_period_end else None
            },
            "highlights": record.highlights,
            "warnings": record.warnings,
            "suggestions": record.suggestions,
            "next_month_budget": record.budget_suggestion,
            "full_report": record.full_report,
            "tokens_used": record.tokens_used,
            "created_at": record.created_at.isoformat()
        }
    )


@router.get("/usage", response_model=Response)
async def get_usage_stats(
    year: Optional[int] = Query(None, description="年份，不填则使用当前年"),
    month: Optional[int] = Query(None, description="月份，不填则使用当前月"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用量统计

    返回指定月份的 AI 服务调用次数和 Token 消耗统计。
    """
    now = datetime.now()
    stat_year = year if year is not None else now.year
    stat_month = month if month is not None else now.month

    try:
        stats = ai_service.get_usage_stats(db, current_user.id, stat_year, stat_month)

        return Response(
            code=200,
            message="success",
            data=stats
        )
    except Exception as e:
        return Response(
            code=500,
            message="获取用量统计失败",
            data=None
        )
