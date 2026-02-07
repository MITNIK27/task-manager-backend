from app.models.task_audit_log import TaskAuditLog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.services.task_service import archive_task, get_task_status_history, restore_task

from app.core.dependencies import get_current_user
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.task_schema import TaskStatus


from app.database import get_db
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from app.services import task_service

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    return task_service.create_task(db, task)

@router.get(
    "/",
    response_model=List[TaskResponse]
)
def get_tasks(db: Session = Depends(get_db)):
    return task_service.get_all_tasks(db)

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_task = task_service.get_task_by_id(db, task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.status:
        validate_role_based_status_change(
            current_user,
            existing_task.status,
            task_data.status
        )
    task = task_service.update_task(db, task_id, task_data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

@router.get("/{task_id}/status-history")
def get_status_history(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task_status_history(db, task_id)

@router.delete("/tasks/{task_id}")
def archive_task_route(task_id: int, db: Session = Depends(get_db)):
    task = archive_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task archived successfully"}


@router.post("/tasks/{task_id}/restore")
def restore_task_route(task_id: int, db: Session = Depends(get_db)):
    task = restore_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task restored successfully"}

@router.get("/tasks/{task_id}/audit-logs")
def get_task_audit_logs(task_id: int, db: Session = Depends(get_db)):
    return (
        db.query(TaskAuditLog)
        .filter(TaskAuditLog.task_id == task_id)
        .order_by(TaskAuditLog.created_at.asc())
        .all()
    )

def validate_role_based_status_change(
    user: User,
    current_status: TaskStatus,
    new_status: TaskStatus
):
    if user.role == UserRole.ADMIN:
        return

    if user.role == UserRole.USER:
        allowed = {
            TaskStatus.TODO: {TaskStatus.IN_PROGRESS},
            TaskStatus.IN_PROGRESS: {TaskStatus.QA_REVIEW},
        }
        if new_status not in allowed.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User cannot perform this status change"
            )

    if user.role == UserRole.QA:
        if current_status != TaskStatus.QA_REVIEW or new_status not in {
            TaskStatus.DONE,
            TaskStatus.TODO
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="QA can only validate or reject tasks"
            )
