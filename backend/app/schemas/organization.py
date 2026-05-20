from pydantic import BaseModel
from datetime import datetime


class OrganizationUpdate(BaseModel):
    organization_name: str = None
    domain: str = None


class OrganizationResponse(BaseModel):
    id: int
    organization_name: str
    domain: str = None
    created_at: datetime

    class Config:
        from_attributes = True
