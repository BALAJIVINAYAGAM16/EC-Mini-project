from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Index
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, index=True)  # admin / manager / employee
    is_active = Column(Boolean, default=True, index=True)
    refresh_token_hash = Column(String, nullable=True, index=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    password_reset_token_hash = Column(String, nullable=True, index=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))


Index("ix_users_role_active", User.role, User.is_active)
