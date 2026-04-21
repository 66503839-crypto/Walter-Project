"""TODO 相关 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str | None = None
    priority: int = Field(0, ge=0, le=2)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    content: str | None = None
    done: bool | None = None
    priority: int | None = Field(None, ge=0, le=2)


class TodoOut(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    done: bool
    created_at: datetime
    updated_at: datetime
