from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApprovalCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ApprovalAction(BaseModel):
    action: str  # approve / reject / hold
    comment: Optional[str] = None


class ApprovalOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    requested_by: int
    status: str
    current_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalHistoryOut(BaseModel):
    id: int
    approval_id: int
    action_by: int
    action: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
