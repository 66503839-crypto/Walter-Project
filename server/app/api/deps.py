"""通用 FastAPI 依赖项。"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import get_db

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 解析当前用户。"""
    payload = decode_token(cred.credentials)
    if payload.get("typ") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 类型错误",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 缺少 sub",
        )

    result = await db.execute(select(User).where(User.id == int(user_id_str)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )
    return user
