"""异步数据库会话。"""
from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """启动时建表（仅开发环境，生产用 Alembic）。"""
    from app.db.base import Base  # noqa: WPS433

    if settings.app_env == "dev":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("📦 数据库表已创建 (dev 模式)")


async def close_db() -> None:
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：获取一个数据库会话。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
