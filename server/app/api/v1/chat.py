"""AI 对话路由。"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models.user import User
from app.schemas.chat import ChatReq, ChatResp
from app.schemas.common import Resp
from app.services.ai import get_ai_provider

router = APIRouter(prefix="/chat", tags=["AI 对话"])


@router.post("", response_model=Resp[ChatResp], summary="AI 对话（非流式）")
async def chat(req: ChatReq, _: User = Depends(get_current_user)):
    provider = get_ai_provider()
    model = req.model or settings.ai_default_model
    content = await provider.chat(req.messages, model, req.temperature)
    return Resp.ok(ChatResp(content=content, model=model, provider=provider.name))


@router.post("/stream", summary="AI 对话（流式 SSE）")
async def chat_stream(req: ChatReq, _: User = Depends(get_current_user)):
    """流式返回 Server-Sent Events：

    每行格式：`data: {"delta": "xxx"}\\n\\n`
    结束标志：`data: [DONE]\\n\\n`
    """
    provider = get_ai_provider()
    model = req.model or settings.ai_default_model

    async def event_stream():
        try:
            async for chunk in provider.chat_stream(req.messages, model, req.temperature):
                yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:  # pragma: no cover
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
