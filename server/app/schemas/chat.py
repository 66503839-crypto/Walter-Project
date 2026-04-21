"""AI 对话 Schema。"""
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatReq(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=40)
    model: str | None = Field(None, description="留空则用服务端默认")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = Field(False, description="是否流式返回")


class ChatResp(BaseModel):
    content: str
    model: str
    provider: str
