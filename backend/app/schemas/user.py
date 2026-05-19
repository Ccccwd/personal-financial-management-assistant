"""
用户相关 Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")


class UserCreate(UserBase):
    """用户创建 Schema"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录 Schema"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新 Schema"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    avatar: Optional[str] = Field(None, description="头像URL")


class ChangePasswordRequest(BaseModel):
    """修改密码请求 Schema"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class PasswordResetRequest(BaseModel):
    """密码重置请求 Schema"""
    email: EmailStr = Field(..., description="邮箱")


class PasswordReset(BaseModel):
    """密码重置确认 Schema"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class ResetPassword(BaseModel):
    """直接重置密码 Schema"""
    email: EmailStr = Field(..., description="邮箱")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 响应 Schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
