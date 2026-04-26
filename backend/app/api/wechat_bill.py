"""
微信账单导入接口
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import base64

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.wechat_bill import ImportPreview
from app.models.user import User
from app.models.import_log import ImportLog
from app.core.dependencies import get_current_active_user
from app.services.wechat_bill_service import WeChatBillService

router = APIRouter()
bill_service = WeChatBillService()


@router.post("/preview", response_model=Response)
async def preview_bill(
    file: UploadFile = File(..., description="微信账单CSV文件"),
    current_user: User = Depends(get_current_active_user),
):
    """
    预览账单文件

    上传微信账单CSV文件，解析后返回预览数据（前10条）和统计摘要。
    """
    if not file.filename or not file.filename.lower().endswith('.csv'):
        return Response(code=400, message="请上传CSV格式文件", data=None)

    try:
        content = await file.read()
        encoding = bill_service._detect_encoding(content)
        csv_content = content.decode(encoding, errors='replace')

        preview = bill_service.parse_csv_content(csv_content)
        preview.filename = file.filename

        return Response(
            code=200,
            message="success",
            data=preview.model_dump()
        )
    except ValueError as e:
        return Response(code=400, message=str(e), data=None)
    except Exception as e:
        return Response(code=500, message=f"解析失败: {str(e)}", data=None)


@router.post("/import", response_model=Response)
async def import_bill(
    file: UploadFile = File(..., description="微信账单CSV文件"),
    account_id: Optional[int] = Form(None, description="导入到指定账户ID"),
    category_id: Optional[int] = Form(None, description="默认分类ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    导入账单（文件上传）

    上传CSV文件并执行导入。支持指定账户和默认分类。
    """
    if not file.filename or not file.filename.lower().endswith('.csv'):
        return Response(code=400, message="请上传CSV格式文件", data=None)

    try:
        content = await file.read()
        encoding = bill_service._detect_encoding(content)
        csv_content = content.decode(encoding, errors='replace')

        # 解析并导入
        preview = bill_service.parse_csv_content(csv_content)
        result = bill_service.import_transactions(
            db, current_user.id, preview.preview_data + (
                bill_service.parse_csv_content(csv_content).preview_data
            ),
            account_id=account_id,
            category_id=category_id,
        )

        # 更新文件名
        import_log = db.query(ImportLog).filter(ImportLog.id == result["import_log_id"]).first()
        if import_log:
            import_log.file_name = file.filename
            db.commit()

        return Response(code=200, message="导入完成", data=result)
    except Exception as e:
        return Response(code=500, message=f"导入失败: {str(e)}", data=None)


@router.post("/import-base64", response_model=Response)
async def import_bill_base64(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    导入账单（Base64编码）

    请求体：{"content": "base64编码的CSV内容", "filename": "xxx.csv", "account_id": 可选}
    """
    content_b64 = data.get("content", "")
    filename = data.get("filename", "bill.csv")
    account_id = data.get("account_id")
    category_id = data.get("category_id")

    if not content_b64:
        return Response(code=400, message="缺少文件内容", data=None)

    try:
        file_bytes = base64.b64decode(content_b64)
        encoding = bill_service._detect_encoding(file_bytes)
        csv_content = file_bytes.decode(encoding, errors='replace')

        preview = bill_service.parse_csv_content(csv_content)

        # 完整解析获取所有记录
        full_preview = bill_service.parse_csv_content(csv_content)

        result = bill_service.import_transactions(
            db, current_user.id, full_preview.preview_data,
            account_id=account_id,
            category_id=category_id,
        )

        import_log = db.query(ImportLog).filter(ImportLog.id == result["import_log_id"]).first()
        if import_log:
            import_log.file_name = filename
            db.commit()

        return Response(code=200, message="导入完成", data=result)
    except Exception as e:
        return Response(code=500, message=f"导入失败: {str(e)}", data=None)


@router.post("/validate", response_model=Response)
async def validate_bill(
    file: UploadFile = File(..., description="微信账单CSV文件"),
    current_user: User = Depends(get_current_active_user),
):
    """
    验证文件格式

    验证上传的文件是否为有效的微信账单CSV格式。
    """
    try:
        content = await file.read()
        result = bill_service.validate_csv_format(content, file.filename or "")
        return Response(
            code=200,
            message="success",
            data=result.model_dump()
        )
    except Exception as e:
        return Response(code=500, message=f"验证失败: {str(e)}", data=None)


@router.get("/import-logs", response_model=Response)
async def get_import_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取导入日志列表"""
    query = db.query(ImportLog).filter(
        ImportLog.user_id == current_user.id
    ).order_by(ImportLog.created_at.desc())

    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "source": log.source,
            "file_name": log.file_name,
            "status": log.status,
            "total_records": log.total_records,
            "success_records": log.success_records,
            "failed_records": log.failed_records,
            "skipped_records": log.skipped_records,
            "import_summary": log.import_summary,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return Response(code=200, message="success", data={
        "logs": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/import-logs/{log_id}", response_model=Response)
async def get_import_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取导入日志详情"""
    log = db.query(ImportLog).filter(
        ImportLog.id == log_id,
        ImportLog.user_id == current_user.id
    ).first()

    if not log:
        return Response(code=404, message="导入日志不存在", data=None)

    return Response(code=200, message="success", data={
        "id": log.id,
        "source": log.source,
        "file_name": log.file_name,
        "file_size": log.file_size,
        "status": log.status,
        "total_records": log.total_records,
        "success_records": log.success_records,
        "failed_records": log.failed_records,
        "skipped_records": log.skipped_records,
        "error_details": log.error_details,
        "import_summary": log.import_summary,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "updated_at": log.updated_at.isoformat() if log.updated_at else None,
    })


@router.get("/import-logs/{log_id}/errors", response_model=Response)
async def get_import_log_errors(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """下载导入错误详情"""
    log = db.query(ImportLog).filter(
        ImportLog.id == log_id,
        ImportLog.user_id == current_user.id
    ).first()

    if not log:
        return Response(code=404, message="导入日志不存在", data=None)

    if not log.error_details:
        return Response(code=200, message="无错误记录", data={"errors": [], "total": 0})

    return Response(code=200, message="success", data={
        "errors": log.error_details,
        "total": len(log.error_details) if isinstance(log.error_details, list) else 0,
    })
