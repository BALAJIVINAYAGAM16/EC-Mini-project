from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String, nullable=False)
    domain = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)