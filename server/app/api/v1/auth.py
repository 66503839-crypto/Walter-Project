"""认证相关路由。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginResp, UserInfo, WxLoginReq
from app.schemas.common import Resp
from app.services.wechat import WechatError, code2session

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/wx-login", response_model=Resp[LoginResp], summary="微信登录")
async def wx_login(req: WxLoginReq, db: AsyncSession = Depends(get_db)):
    """小程序登录流程：

    1. 前端 `wx.login()` 获取临时 code
    2. 前端调用本接口，带上 code 和可选的昵称/头像
    3. 后端用 code 调微信 `jscode2session` 换取 openid
    4. upsert User 记录
    5. 签发 JWT 返回
    """
    try:
        wx_data = await code2session(req.code)
    except WechatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {e.errmsg}",
        )

    openid = wx_data["openid"]
    unionid = wx_data.get("unionid")

    # upsert
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            openid=openid,
            unionid=unionid,
            nickname=req.nickname,
            avatar=req.avatar,
        )
        db.add(user)
    else:
        if req.nickname:
            user.nickname = req.nickname
        if req.avatar:
            user.avatar = req.avatar
        if unionid and not user.unionid:
            user.unionid = unionid

    await db.commit()
    await db.refresh(user)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return Resp.ok(
        LoginResp(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.jwt_access_ttl_minutes * 60,
            user=UserInfo(
                id=user.id,
                openid=user.openid,
                nickname=user.nickname,
                avatar=user.avatar,
                preferred_provider=user.preferred_provider,
            ),
        )
    )


@router.post("/refresh", response_model=Resp[dict], summary="刷新 Access Token")
async def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload.get("typ") != "refresh":
        raise HTTPException(status_code=400, detail="非 refresh token")
    access = create_access_token(payload["sub"])
    return Resp.ok({"access_token": access, "expires_in": settings.jwt_access_ttl_minutes * 60})
