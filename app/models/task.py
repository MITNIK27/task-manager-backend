from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="TODO", nullable=False)
    priority = Column(String, default="MEDIUM", nullable=False)
    due_date = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ✅ DUPLICATE FIELDS (MUST BE INSIDE CLASS)
    is_duplicate = Column(Boolean, default=False, nullable=False)
    duplicate_of_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    duplicate_of = relationship("Task", remote_side=[id])

    is_archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)