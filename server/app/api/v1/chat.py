"""AI 对话路由。"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models.user import User
from app.schemas.chat import ChatMessage, ChatReq, ChatResp, ProviderInfo
from app.schemas.common import Resp
from app.services.ai import AVAILABLE_PROVIDERS, get_ai_provider

router = APIRouter(prefix="/chat", tags=["AI 对话"])


# MiniGamer 的人设。放在每次对话最前面，让模型以此口吻回答。
SYSTEM_PROMPT = (
    "你是 MiniGamer 助手——一个内嵌在微信小程序里的综合型个人助手，"
    "由用户自己开发和部署。"
    "你的口吻要轻松、友好、有点幽默感；回答要简洁明了，避免冗长说教。"
    "如果被问到你是谁、你是什么模型、你是哪家公司开发的，"
    "就回答『我是 MiniGamer 助手，你的私人小帮手 🤖』，不要提底层供应商名字。"
    "如果用户问其他问题，正常回答即可。"
)


def _with_system_prompt(messages: list[ChatMessage]) -> list[ChatMessage]:
    """若首条不是 system 消息，则前置注入 MiniGamer 人设。"""
    if messages and messages[0].role == "system":
        return messages
    return [ChatMessage(role="system", content=SYSTEM_PROMPT), *messages]


def _resolve_provider_name(req_provider: str | None, user: User) -> str | None:
    """按优先级解析要用的 provider 名：请求 > 用户偏好 > 服务端默认。"""
    return req_provider or user.preferred_provider or None


@router.get(
    "/providers",
    response_model=Resp[list[ProviderInfo]],
    summary="列出所有可选的 AI Provider",
)
async def list_providers(_: User = Depends(get_current_user)):
    return Resp.ok([ProviderInfo(**p) for p in AVAILABLE_PROVIDERS])


@router.post("", response_model=Resp[ChatResp], summary="AI 对话（非流式）")
async def chat(req: ChatReq, user: User = Depends(get_current_user)):
    provider_name = _resolve_provider_name(req.provider, user)
    provider = get_ai_provider(provider_name)
    model = req.model or settings.ai_default_model
    msgs = _with_system_prompt(req.messages)
    content = await provider.chat(msgs, model, req.temperature)
    return Resp.ok(ChatResp(content=content, model=model, provider=provider.name))


@router.post("/stream", summary="AI 对话（流式 SSE）")
async def chat_stream(req: ChatReq, user: User = Depends(get_current_user)):
    """流式返回 Server-Sent Events：

    每行格式：`data: {"delta": "xxx"}\\n\\n`
    结束标志：`data: [DONE]\\n\\n`
    """
    provider_name = _resolve_provider_name(req.provider, user)
    provider = get_ai_provider(provider_name)
    model = req.model or settings.ai_default_model
    msgs = _with_system_prompt(req.messages)

    async def event_stream():
        try:
            async for chunk in provider.chat_stream(msgs, model, req.temperature):
                yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:  # pragma: no cover
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
