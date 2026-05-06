from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)  # admin / manager / employee
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)