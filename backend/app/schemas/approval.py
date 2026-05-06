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
    status: str
    current_level: str
    created_at: datetime

    class Config:
        from_attributes = True