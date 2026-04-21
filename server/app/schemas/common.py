"""通用响应 Schema。"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Resp(BaseModel, Generic[T]):
    """统一响应体。"""

    code: int = Field(0, description="0=成功，非 0=业务错误码")
    message: str = Field("ok", description="提示信息")
    data: T | None = Field(None, description="业务数据")

    @classmethod
    def ok(cls, data: Any = None, message: str = "ok") -> "Resp":
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, code: int = 1, message: str = "error", data: Any = None) -> "Resp":
        return cls(code=code, message=message, data=data)
