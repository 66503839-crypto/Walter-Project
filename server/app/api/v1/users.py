"""用户信息路由。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import UserInfo, UserUpdateReq
from app.schemas.common import Resp
from app.services.ai import is_valid_provider

router = APIRouter(prefix="/users", tags=["用户"])


def _to_info(user: User) -> UserInfo:
    return UserInfo(
        id=user.id,
        openid=user.openid,
        nickname=user.nickname,
        avatar=user.avatar,
        preferred_provider=user.preferred_provider,
    )


@router.get("/me", response_model=Resp[UserInfo], summary="获取当前用户信息")
async def me(user: User = Depends(get_current_user)):
    return Resp.ok(_to_info(user))


@router.patch("/me", response_model=Resp[UserInfo], summary="更新当前用户偏好")
async def update_me(
    payload: UserUpdateReq,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatar is not None:
        user.avatar = payload.avatar
    if payload.preferred_provider is not None:
        # 空串表示清除（回退到服务端默认）
        if payload.preferred_provider == "":
            user.preferred_provider = None
        elif is_valid_provider(payload.preferred_provider):
            user.preferred_provider = payload.preferred_provider
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的 provider: {payload.preferred_provider}",
            )
    await db.commit()
    await db.refresh(user)
    return Resp.ok(_to_info(user))
