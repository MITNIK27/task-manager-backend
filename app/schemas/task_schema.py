from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.schemas.task_enums import TaskStatus, TaskPriority
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None



class TaskCreate(TaskBase):
    pass



class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

    is_duplicate: Optional[bool] = None
    duplicate_of_task_id: Optional[int] = None

    is_archived: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    is_duplicate: bool
    duplicate_of_task_id: Optional[int]
    
    is_archived: bool
    archived_at: Optional[datetime]

    class Config:
        from_attributes = True


