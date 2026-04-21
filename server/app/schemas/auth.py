"""认证相关 Schema。"""
from pydantic import BaseModel, Field


class WxLoginReq(BaseModel):
    """微信登录请求。"""

    code: str = Field(..., description="wx.login 返回的临时 code")
    nickname: str | None = Field(None, description="用户昵称（可选）")
    avatar: str | None = Field(None, description="用户头像 URL（可选）")


class UserInfo(BaseModel):
    id: int
    openid: str
    nickname: str | None = None
    avatar: str | None = None


class LoginResp(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="access_token 过期秒数")
    user: UserInfo
