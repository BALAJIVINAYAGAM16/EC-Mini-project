from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)

    requested_by = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="pending")  # pending / approved / rejected
    current_level = Column(String, default="manager")  # manager → admin

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")