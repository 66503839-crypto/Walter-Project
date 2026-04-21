"""TODO 增删改查（示例业务）。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.todo import Todo
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import Resp
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(prefix="/todos", tags=["TODO"])


@router.get("", response_model=Resp[list[TodoOut]], summary="列出我的 TODO")
async def list_todos(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Todo).where(Todo.user_id == user.id).order_by(desc(Todo.created_at))
    )
    todos = result.scalars().all()
    return Resp.ok([TodoOut.model_validate(t) for t in todos])


@router.post("", response_model=Resp[TodoOut], summary="创建 TODO")
async def create_todo(
    payload: TodoCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = Todo(user_id=user.id, **payload.model_dump())
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return Resp.ok(TodoOut.model_validate(todo))


@router.patch("/{todo_id}", response_model=Resp[TodoOut], summary="更新 TODO")
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await _get_owned(db, todo_id, user.id)
    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(todo, k, v)
    await db.commit()
    await db.refresh(todo)
    return Resp.ok(TodoOut.model_validate(todo))


@router.delete("/{todo_id}", response_model=Resp[dict], summary="删除 TODO")
async def delete_todo(
    todo_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await _get_owned(db, todo_id, user.id)
    await db.delete(todo)
    await db.commit()
    return Resp.ok({"id": todo_id})


async def _get_owned(db: AsyncSession, todo_id: int, user_id: int) -> Todo:
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    )
    todo = result.scalar_one_or_none()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TODO 不存在")
    return todo
