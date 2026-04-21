"""用户模型。"""
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 微信 openid（小程序内唯一标识）
    openid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # 微信 unionid（跨应用唯一标识，可能为空）
    unionid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    # 昵称 / 头像（由前端调用 wx.getUserProfile 后传上来）
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} openid={self.openid[:8]}...>"
