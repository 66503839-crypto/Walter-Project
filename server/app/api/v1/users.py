"""用户信息路由。"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.auth import UserInfo
from app.schemas.common import Resp

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=Resp[UserInfo], summary="获取当前用户信息")
async def me(user: User = Depends(get_current_user)):
    return Resp.ok(
        UserInfo(
            id=user.id,
            openid=user.openid,
            nickname=user.nickname,
            avatar=user.avatar,
        )
    )
