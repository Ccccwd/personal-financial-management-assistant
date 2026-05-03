"""
认证接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config.database import get_db
from app.config.settings import settings
from app.schemas.common import Response
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserUpdate, ChangePasswordRequest, PasswordResetRequest,
    PasswordReset, ResetPassword
)
from app.models.user import User
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_refresh_token,
    create_password_reset_token, verify_password_reset_token
)
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=Response[dict])
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


@router.post("/login", response_model=Response[dict])
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

    # 生成 Access Token 和 Refresh Token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )

    return Response(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    )


@router.get("/me", response_model=Response[dict])
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return Response(
        code=200,
        message="success",
        data=UserResponse.model_validate(current_user).model_dump()
    )


@router.post("/logout", response_model=Response[None])
async def logout(current_user: User = Depends(get_current_active_user)):
    """用户登出"""
    # 由于 FastAPI 的依赖注入机制，token 无法直接传递
    # 这里返回提示，客户端应该删除本地存储的 token
    # 实际的黑名单功能需要在中间件或自定义依赖中实现
    return Response(
        code=200,
        message="登出成功",
        data=None
    )


@router.post("/refresh", response_model=Response[dict])
async def refresh_token(
    refresh_token: str = Query(..., description="刷新令牌"),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        return Response(code=401, message="无效的刷新令牌", data=None)

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return Response(code=401, message="无效的刷新令牌", data=None)

    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        return Response(code=401, message="无效的刷新令牌", data=None)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return Response(code=401, message="用户不存在或已被禁用", data=None)

    # 生成新的访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Response(
        code=200,
        message="令牌刷新成功",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        ).model_dump()
    )


@router.put("/me", response_model=Response[dict])
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 更新用户名
    if user_data.username is not None:
        # 检查用户名是否被其他用户占用
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            return Response(code=400, message="用户名已被使用", data=None)
        current_user.username = user_data.username

    # 更新头像
    if user_data.avatar is not None:
        current_user.avatar = user_data.avatar

    db.commit()
    db.refresh(current_user)

    return Response(
        code=200,
        message="用户信息更新成功",
        data=UserResponse.model_validate(current_user).model_dump()
    )


@router.post("/change-password", response_model=Response[None])
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        return Response(code=400, message="旧密码错误", data=None)

    # 检查新密码是否与旧密码相同
    if verify_password(password_data.new_password, current_user.password_hash):
        return Response(code=400, message="新密码不能与旧密码相同", data=None)

    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return Response(
        code=200,
        message="密码修改成功",
        data=None
    )


@router.post("/password-reset-request", response_model=Response[dict])
async def password_reset_request(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """请求密码重置"""
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        return Response(code=404, message="邮箱未注册", data=None)

    # 生成密码重置令牌（有效期15分钟）
    reset_token = create_password_reset_token(user.id)

    return Response(
        code=200,
        message="密码重置令牌已生成",
        data={"token": reset_token}
    )


@router.post("/password-reset", response_model=Response[None])
async def password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """使用令牌重置密码"""
    user_id = verify_password_reset_token(reset_data.token)
    if user_id is None:
        return Response(code=401, message="无效或过期的重置令牌", data=None)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response(code=404, message="用户不存在", data=None)

    # 更新密码
    user.password_hash = get_password_hash(reset_data.new_password)
    db.commit()

    return Response(
        code=200,
        message="密码重置成功",
        data=None
    )


@router.post("/reset-password", response_model=Response[None])
async def reset_password(
    reset_data: ResetPassword,
    db: Session = Depends(get_db)
):
    """直接重置密码（无需令牌）"""
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        return Response(code=404, message="邮箱未注册", data=None)

    # 更新密码
    user.password_hash = get_password_hash(reset_data.new_password)
    db.commit()

    return Response(
        code=200,
        message="密码重置成功",
        data=None
    )
