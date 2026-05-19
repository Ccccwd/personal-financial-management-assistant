"""
提醒管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.config.database import get_db
from app.schemas.common import Response
from app.schemas.reminder import (
    ReminderCreate, ReminderUpdate, ReminderResponse,
    ReminderStatistics, ReminderListResponse
)
from app.models.user import User
from app.models.reminder import Reminder
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=Response)
async def get_reminders(
    reminder_type: Optional[str] = Query(None, description="提醒类型"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Reminder).filter(Reminder.user_id == current_user.id)

    if reminder_type:
        query = query.filter(Reminder.type == reminder_type)

    if is_enabled is not None:
        query = query.filter(Reminder.is_enabled == is_enabled)

    reminders = query.order_by(Reminder.created_at.desc()).all()

    return Response(
        code=200,
        message="success",
        data=ReminderListResponse(
            reminders=[ReminderResponse.model_validate(r) for r in reminders],
            total=len(reminders)
        ).model_dump()
    )


@router.get("/statistics", response_model=Response)
async def get_reminder_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    total = db.query(Reminder).filter(Reminder.user_id == current_user.id).count()
    enabled = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_enabled
    ).count()
    disabled = total - enabled

    return Response(
        code=200,
        message="success",
        data=ReminderStatistics(
            total=total,
            enabled=enabled,
            disabled=disabled
        ).model_dump()
    )


@router.get("/check-today", response_model=Response)
async def check_today_reminders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    current_time = now.time()
    current_day = now.day

    query = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_enabled
    )

    reminders = query.all()
    triggered_reminders = []

    for reminder in reminders:
        should_trigger = False

        if reminder.type == "daily" and reminder.remind_time:
            reminder_time = datetime.strptime(str(reminder.remind_time), "%H:%M:%S").time()
            if reminder_time.hour == current_time.hour:
                should_trigger = True

        elif reminder.type == "budget" and reminder.remind_day:
            if reminder.remind_day == current_day:
                should_trigger = True

        elif reminder.type == "recurring" and reminder.remind_day:
            if reminder.remind_day == current_day:
                should_trigger = True

        elif reminder.type == "report" and reminder.remind_day:
            if reminder.remind_day == current_day:
                should_trigger = True

        if should_trigger:
            triggered_reminders.append(ReminderResponse.model_validate(reminder))

    return Response(
        code=200,
        message="success",
        data={
            "reminders": [r.model_dump() for r in triggered_reminders],
            "total": len(triggered_reminders),
            "current_time": current_time.strftime("%H:%M:%S"),
            "current_day": current_day
        }
    )


@router.get("/{reminder_id}", response_model=Response)
async def get_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        return Response(code=404, message="提醒不存在", data=None)

    return Response(
        code=200,
        message="success",
        data=ReminderResponse.model_validate(reminder).model_dump()
    )


@router.post("", response_model=Response)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    remind_time_obj = None
    if reminder_data.remind_time:
        try:
            remind_time_obj = datetime.strptime(reminder_data.remind_time, "%H:%M:%S").time()
        except ValueError:
            return Response(code=400, message="时间格式错误", data=None)

    reminder = Reminder(
        user_id=current_user.id,
        type=reminder_data.type,
        title=reminder_data.title,
        content=reminder_data.content,
        remind_time=remind_time_obj,
        remind_day=reminder_data.remind_day,
        category_id=reminder_data.category_id,
        amount=reminder_data.amount,
        is_enabled=reminder_data.is_enabled
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return Response(
        code=200,
        message="创建成功",
        data=ReminderResponse.model_validate(reminder).model_dump()
    )


@router.put("/{reminder_id}", response_model=Response)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        return Response(code=404, message="提醒不存在", data=None)

    update_data = reminder_data.model_dump(exclude_unset=True)

    if "remind_time" in update_data and update_data["remind_time"]:
        try:
            update_data["remind_time"] = datetime.strptime(
                update_data["remind_time"], "%H:%M:%S"
            ).time()
        except ValueError:
            return Response(code=400, message="时间格式错误", data=None)

    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)

    return Response(
        code=200,
        message="更新成功",
        data=ReminderResponse.model_validate(reminder).model_dump()
    )


@router.patch("/{reminder_id}/toggle", response_model=Response)
async def toggle_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        return Response(code=404, message="提醒不存在", data=None)

    reminder.is_enabled = not reminder.is_enabled
    db.commit()
    db.refresh(reminder)

    status_text = "启用" if reminder.is_enabled else "禁用"

    return Response(
        code=200,
        message=f"{status_text}成功",
        data=ReminderResponse.model_validate(reminder).model_dump()
    )


@router.delete("/{reminder_id}", response_model=Response)
async def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        return Response(code=404, message="提醒不存在", data=None)

    db.delete(reminder)
    db.commit()

    return Response(
        code=200,
        message="删除成功",
        data=None
    )
