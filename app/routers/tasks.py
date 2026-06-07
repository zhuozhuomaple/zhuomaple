from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.database import get_db
from app.models import Task
from app.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _apply_list_filters(
    query: Select,
    *,
    status: TaskStatus | None,
    priority: TaskPriority | None,
    start_date: date | None,
    end_date: date | None,
) -> Select:
    if status is not None:
        query = query.where(Task.status == status.value)
    if priority is not None:
        query = query.where(Task.priority == priority.value)
    if start_date is not None:
        query = query.where(Task.created_at >= start_date)
    if end_date is not None:
        query = query.where(Task.created_at <= end_date)
    return query


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=payload.title,
        status=payload.status.value,
        priority=payload.priority.value,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = Query(None, description="按状态过滤"),
    priority: TaskPriority | None = Query(None, description="按优先级过滤"),
    start_date: date | None = Query(None, description="起始日期（含），格式 YYYY-MM-DD"),
    end_date: date | None = Query(None, description="结束日期（含），格式 YYYY-MM-DD"),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    filters = {
        "status": status,
        "priority": priority,
        "start_date": start_date,
        "end_date": end_date,
    }

    query = _apply_list_filters(select(Task), **filters)
    count_query = _apply_list_filters(select(func.count()).select_from(Task), **filters)

    total = db.scalar(count_query) or 0

    order = Task.created_at.asc() if sort == "asc" else Task.created_at.desc()
    query = query.order_by(order).offset((page - 1) * page_size).limit(page_size)

    items = db.scalars(query).all()
    return TaskListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_task_or_404(task_id, db)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_task_or_404(task_id, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"status", "priority"} and value is not None:
            setattr(task, field, value.value)
        else:
            setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()
    return None
