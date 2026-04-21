"""SQLAlchemy 声明基类。"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.sqlite import INTEGER as SQLITE_INTEGER
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import BigInteger

# 让 BigInteger 在 SQLite 下编译为 INTEGER，使其成为 rowid 别名从而支持 autoincrement。
# PostgreSQL 等其他数据库保持 BIGINT 不变。
@compiles(BigInteger, "sqlite")
def _bigint_as_integer_on_sqlite(element, compiler, **kw):  # noqa: ARG001
    return "INTEGER"


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


class TimestampMixin:
    """统一时间戳字段。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
