from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.admin_guard import require_admin
from app.services.task_service import get_task_by_id
from app.services.audit_service import create_audit_log
from app.schemas.task_schema import TaskStatus

router = APIRouter(
    prefix="/qa",
    tags=["QA"]
)

@router.post("/tasks/{task_id}/approve")
def qa_approve_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)  # reuse admin guard for now
):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail="Only DONE tasks can be approved by QA"
        )

    create_audit_log(
        db=db,
        task_id=task.id,
        action="QA_APPROVED",
        old_value=TaskStatus.DONE,
        new_value=TaskStatus.DONE
    )

    db.commit()

    return {"message": "Task approved by QA"}

@router.post("/tasks/{task_id}/reject")
def qa_reject_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail="Only DONE tasks can be rejected by QA"
        )

    task.status = TaskStatus.TODO

    create_audit_log(
        db=db,
        task_id=task.id,
        action="QA_REJECTED",
        old_value=TaskStatus.DONE,
        new_value=TaskStatus.TODO
    )

    db.commit()
    db.refresh(task)

    return {"message": "Task rejected and sent back to TODO"}
