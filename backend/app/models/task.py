from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.database import Base
import datetime
 
class Task(Base):
    __tablename__ = "tasks"
 
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="todo")
    priority = Column(String, default="medium")
    due_date = Column(DateTime) # Deadline
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)