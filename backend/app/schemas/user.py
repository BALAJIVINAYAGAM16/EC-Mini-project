from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str = "Balaji"
    email: str = "balaji200116@gmail.com"
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str = "balaji200116@gmail.com"
    password: str = "123456"


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime


    class Config:
        from_attributes = True
