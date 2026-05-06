from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    status = Column(
        Enum("todo", "in_progress", "review", "done", name="task_status"),
        default="todo"
    )

    priority = Column(String, default="medium")
    due_date = Column(DateTime)

    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # NEW

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

    @property
    def assigned_to_name(self):
        return self.assigned_to.name if self.assigned_to else None
    
    
class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer)
    old_status = Column(String)
    new_status = Column(String)
    changed_by = Column(Integer)

    changed_at = Column(DateTime, default=datetime.datetime.utcnow)