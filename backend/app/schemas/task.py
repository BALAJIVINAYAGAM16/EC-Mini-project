from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

    
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"   # ADD THIS
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


def _validate_future_due_date(value: Optional[datetime]):
    if value and value < datetime.utcnow():
        raise ValueError("Due date cannot be in the past")
    return value


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value


class TaskCreate(TaskBase):
    assigned_to_id: Optional[int] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Optional[datetime]):
        return _validate_future_due_date(value)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]):
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Optional[datetime]):
        return _validate_future_due_date(value)


class TaskAssign(BaseModel):
    assigned_to_id: int


class TaskOut(TaskBase):
    id: int
    created_by_id: int
    assigned_to_id: Optional[int]
    assigned_to_name: Optional[str] = None

    updated_by: Optional[int] = None  # ADD THIS

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status: TaskStatus
