from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)

    status = Column(
        Enum("todo", "in_progress", "review", "done", name="task_status"),
        default="todo"
    )

    priority = Column(String, default="medium", index=True)
    due_date = Column(DateTime, index=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # NEW

    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, index=True)

    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

    @property
    def assigned_to_name(self):
        return self.assigned_to.name if self.assigned_to else None
    
    
class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True)
    old_status = Column(String)
    new_status = Column(String)
    changed_by = Column(Integer, index=True)

    changed_at = Column(DateTime, default=datetime.datetime.utcnow)


Index("ix_tasks_assigned_status_updated", Task.assigned_to_id, Task.status, Task.updated_at)
Index("ix_tasks_created_status_updated", Task.created_by_id, Task.status, Task.updated_at)
