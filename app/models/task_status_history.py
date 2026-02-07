from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class TaskStatusHistory(Base):
    __tablename__ = "task_status_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
