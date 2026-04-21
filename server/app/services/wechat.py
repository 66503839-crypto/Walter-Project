"""微信小程序服务端交互。"""
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings


class WechatError(Exception):
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[WeChat {errcode}] {errmsg}")


async def code2session(code: str) -> dict[str, Any]:
    """用 code 换取 openid / session_key / unionid。

    微信官方文档: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    url = f"{settings.wechat_api_base}/sns/jscode2session"
    params = {
        "appid": settings.wechat_appid,
        "secret": settings.wechat_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    # 开发阶段：若未配置微信凭据，返回模拟数据便于联调
    if not settings.wechat_appid or settings.wechat_appid == "wx_replace_me":
        logger.warning("⚠️  WECHAT_APPID 未配置，返回 mock openid（仅用于开发）")
        return {
            "openid": f"mock_openid_{code[:8]}",
            "session_key": "mock_session_key",
            "unionid": None,
        }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise WechatError(data["errcode"], data.get("errmsg", "unknown"))

    return data
