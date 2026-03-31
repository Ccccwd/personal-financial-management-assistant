"""
认证接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config.database import get_db
from app.config.settings import settings
from app.schemas.common import Response
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=Response)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return Response(code=400, message="用户名已存在", data=None)

    # 检查邮箱是否存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        return Response(code=400, message="邮箱已被注册", data=None)

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return Response(
        code=200,
        message="注册成功",
        data=UserResponse.model_validate(user).model_dump()
    )


@router.post("/login", response_model=Response)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        return Response(code=401, message="用户名或密码错误", data=None)

    if not user.is_active:
        return Response(code=403, message="账户已被禁用", data=None)

    # 生成 Token（JWT 规范要求 sub 必须为字符串）
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Response(
        code=200,
        message="登录成功",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        ).model_dump()
    )


@router.get("/me", response_model=Response)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return Response(
        code=200,
        message="success",
        data=UserResponse.model_validate(current_user).model_dump()
    )
