import datetime
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskStatus
from fastapi import HTTPException, status
from app.models.task_status_history import TaskStatusHistory
from app.services.audit_service import create_audit_log


def create_task(db: Session, task_data: TaskCreate) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

def get_all_tasks(db: Session, include_archived: bool = False):
    query = db.query(Task)

    if not include_archived:
        query = query.filter(Task.is_archived == False)

    return query.all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def close_duplicate_tasks(db: Session, original_task_id: int):
    duplicate_tasks = (
        db.query(Task)
        .filter(
            Task.is_duplicate == True,
            Task.duplicate_of_task_id == original_task_id,
            Task.status != TaskStatus.DONE
        )
        .all()
    )

    for dup_task in duplicate_tasks:
        dup_task.status = TaskStatus.DONE


def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    task = get_task_by_id(db, task_id)

    if not task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)

    # 1️⃣ STATUS TRANSITION VALIDATION
    if "status" in update_data:
        validate_status_transition(task.status, update_data["status"])

        if update_data["status"] != task.status:

            # 🔔 Determine semantic action
            if task.status == TaskStatus.IN_PROGRESS and update_data["status"] == TaskStatus.DONE:
                action = "MOVED_TO_QA"
            elif task.status == TaskStatus.DONE and update_data["status"] == TaskStatus.DONE:
                action = "QA_APPROVED"
            elif task.status == TaskStatus.DONE and update_data["status"] == TaskStatus.TODO:
                action = "QA_REJECTED"
            else:
                action = "STATUS_CHANGED"

            create_audit_log(
                db=db,
                task_id=task.id,
                action=action,
                old_value=task.status,
                new_value=update_data["status"]
            )

            db.add(
                TaskStatusHistory(
                    task_id=task.id,
                    old_status=task.status,
                    new_status=update_data["status"]
                )
            )

        
    # 🔔 PRIORITY CHANGE AUDIT
    if "priority" in update_data and update_data["priority"] != task.priority:
            create_audit_log(
                db=db,
                task_id=task.id,
                action="PRIORITY_CHANGED",
                old_value=task.priority,
                new_value=update_data["priority"]
            )   


    # 2️⃣ DUPLICATE VALIDATION
    if update_data.get("is_duplicate"):
        if not update_data.get("duplicate_of_task_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="duplicate_of_task_id must be provided when marking a task as duplicate"
            )

        original_task = get_task_by_id(db, update_data["duplicate_of_task_id"])

        if not original_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original task for duplication not found"
            )

        if original_task.id == task.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot be marked as duplicate of itself"
            )

    # 3️⃣ APPLY UPDATES
    for field, value in update_data.items():
        setattr(task, field, value)

    # 4️⃣ AUTO‑CLOSE DUPLICATES
    if (
        "status" in update_data
        and update_data["status"] == TaskStatus.DONE
        and not task.is_duplicate
    ):
        close_duplicate_tasks(db, task.id)

    # 5️⃣ SINGLE COMMIT (task + audit together)
    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task_by_id(db, task_id)

    if not task:
        return False

    db.delete(task)
    db.commit()

    return True

def archive_task(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        return None

    if task.is_archived:
        return task

    task.is_archived = True
    task.archived_at = datetime.utcnow()

    create_audit_log(
        db=db,
        task_id=task.id,
        action="ARCHIVED"
    )

    db.commit()
    db.refresh(task)

    return task



def restore_task(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        return None

    if not task.is_archived:
        return task

    task.is_archived = False
    task.archived_at = None

    create_audit_log(
        db=db,
        task_id=task.id,
        action="RESTORED"
    )

    db.commit()
    db.refresh(task)

    return task




ALLOWED_STATUS_TRANSITIONS = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS},

    TaskStatus.IN_PROGRESS: {
        TaskStatus.TODO,
        TaskStatus.QA_REVIEW,   # 🔹 submit for QA
    },

    TaskStatus.QA_REVIEW: {
        TaskStatus.DONE,       # ✅ approved by QA
        TaskStatus.TODO,       # ❌ rejected → rework
    },

    TaskStatus.DONE: set()
}


def validate_status_transition(current_status: TaskStatus, new_status: TaskStatus):
    allowed_next_states = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    if new_status not in allowed_next_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )


def get_task_status_history(db: Session, task_id: int):
    return (
        db.query(TaskStatusHistory)
        .filter(TaskStatusHistory.task_id == task_id)
        .order_by(TaskStatusHistory.timestamp.asc())
        .all()
    )

