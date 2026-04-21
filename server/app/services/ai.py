"""AI Provider 抽象 + 工厂。

所有 Provider 统一通过 OpenAI 兼容协议（DeepSeek、通义都支持），
这样只需一份代码即可切换。
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.chat import ChatMessage


class BaseAIProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def chat(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> str: ...

    @abstractmethod
    async def chat_stream(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> AsyncGenerator[str, None]: ...


class OpenAICompatProvider(BaseAIProvider):
    """OpenAI 兼容 Provider（DeepSeek、通义、OpenAI 通用）。"""

    def __init__(self, name: str, api_key: str, base_url: str, default_model: str):
        self.name = name
        self.default_model = default_model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> str:
        resp = await self._client.chat.completions.create(
            model=model or self.default_model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    async def chat_stream(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> AsyncGenerator[str, None]:
        stream = await self._client.chat.completions.create(
            model=model or self.default_model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta


class MockProvider(BaseAIProvider):
    """Mock Provider（未配置真实 API Key 时使用）。"""

    name = "mock"

    async def chat(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> str:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        return f"[Mock 回复] 你说的是: {last_user}\n\n（请在 .env 配置 AI_PROVIDER 以启用真实 AI）"

    async def chat_stream(
        self, messages: list[ChatMessage], model: str, temperature: float
    ) -> AsyncGenerator[str, None]:
        text = await self.chat(messages, model, temperature)
        for ch in text:
            yield ch


def get_ai_provider() -> BaseAIProvider:
    provider = settings.ai_provider
    if provider == "openai":
        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY 未配置，回退到 mock")
            return MockProvider()
        return OpenAICompatProvider(
            "openai",
            settings.openai_api_key,
            settings.openai_base_url,
            settings.ai_default_model,
        )
    if provider == "deepseek":
        if not settings.deepseek_api_key:
            logger.warning("DEEPSEEK_API_KEY 未配置，回退到 mock")
            return MockProvider()
        return OpenAICompatProvider(
            "deepseek",
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            "deepseek-chat",
        )
    if provider == "qwen":
        if not settings.qwen_api_key:
            logger.warning("QWEN_API_KEY 未配置，回退到 mock")
            return MockProvider()
        return OpenAICompatProvider(
            "qwen",
            settings.qwen_api_key,
            settings.qwen_base_url,
            "qwen-plus",
        )
    return MockProvider()
