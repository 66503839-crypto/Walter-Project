"""应用配置（从 .env 读取，使用 pydantic-settings）。"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 应用 ----------
    app_env: Literal["dev", "prod"] = "dev"
    app_name: str = "MiniGamer"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # ---------- 数据库 ----------
    database_url: str = "postgresql+asyncpg://minigamer:change_me@127.0.0.1:5432/minigamer"

    # ---------- Redis ----------
    redis_url: str = "redis://127.0.0.1:6379/0"

    # ---------- JWT ----------
    jwt_secret_key: str = "change_me_in_prod_min_32_chars_abcdefghijklmnop"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 60
    jwt_refresh_ttl_days: int = 30

    # ---------- 微信 ----------
    wechat_appid: str = ""
    wechat_secret: str = ""
    wechat_api_base: str = "https://api.weixin.qq.com"

    # ---------- AI ----------
    ai_provider: Literal["openai", "deepseek", "qwen", "tokenplan", "mock"] = "mock"
    ai_default_model: str = "gpt-4o-mini"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 腾讯云 TokenPlan（OpenAI 兼容协议）
    tokenplan_api_key: str = ""
    tokenplan_base_url: str = "https://api.lkeap.cloud.tencent.com/plan/v3"
    tokenplan_default_model: str = "tc-code-latest"

    # ---------- CORS ----------
    cors_origins: str = "http://localhost:3000,https://servicewechat.com"

    # ---------- 日志 ----------
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
