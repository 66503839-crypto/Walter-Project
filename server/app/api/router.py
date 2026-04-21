"""v1 路由注册。"""
from fastapi import APIRouter

from app.api.v1 import auth, chat, todos, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(todos.router)
api_router.include_router(chat.router)
