from pydantic import BaseModel
from typing import Optional
from datetime import datetime
 
# 🔹 Base schema
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None
 
 
# 🔹 Request: Create task
class TaskCreate(TaskBase):
    assigned_to_id: Optional[int] = None  # Optional for creation
 
 
# 🔹 Request: Update task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
 
 
class TaskAssign(BaseModel):
    assigned_to_id: int
 
 
# 🔹 Response: Task output
class TaskOut(TaskBase):
    id: int
    created_by_id: int
    assigned_to_id: Optional[int]
    created_at: datetime
 
    class Config:
        from_attributes = True