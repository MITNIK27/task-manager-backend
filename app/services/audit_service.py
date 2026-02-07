from sqlalchemy.orm import Session
from app.models.task_audit_log import TaskAuditLog


def create_audit_log(
    db: Session,
    task_id: int,
    action: str,
    old_value: str | None = None,
    new_value: str | None = None
):
    log = TaskAuditLog(
        task_id=task_id,
        action=action,
        old_value=old_value,
        new_value=new_value
    )

    db.add(log)

def get_all_audit_logs(db: Session):
    return (
        db.query(TaskAuditLog)
        .order_by(TaskAuditLog.created_at.desc())
        .all()
    )