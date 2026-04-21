"""MiniGamer 服务端主入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动与关闭钩子。"""
    setup_logging()
    logger.info(f"🚀 {settings.app_name} 启动中... env={settings.app_env}")
    await init_db()
    yield
    logger.info("👋 应用关闭中...")
    await close_db()


app = FastAPI(
    title=settings.app_name,
    description="微信小程序助手 MiniGamer 的后端 API",
    version="0.1.0",
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "ok",
        "docs": "/docs" if settings.app_debug else "disabled",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
