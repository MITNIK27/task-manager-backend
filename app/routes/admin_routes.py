from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.admin_guard import require_admin
from app.services.audit_service import get_all_audit_logs
from app.services.task_service import get_all_tasks
from app.services.task_service import update_task, get_task_by_id
from app.schemas.task_schema import TaskUpdate
from app.schemas.task_schema import TaskStatus


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/tasks")
def admin_get_all_tasks(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return get_all_tasks(db, include_archived=True)

@router.get("/audit-logs")
def admin_get_audit_logs(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return get_all_audit_logs(db)

@router.put("/tasks/{task_id}/status")
def admin_force_update_task_status(
    task_id: int,
    status_data: TaskUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if not status_data.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )

    # Admin bypasses role-based restrictions
    task.status = status_data.status

    db.commit()
    db.refresh(task)

    return task
