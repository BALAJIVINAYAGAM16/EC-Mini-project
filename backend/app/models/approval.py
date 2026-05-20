from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)

    requested_by = Column(Integer, ForeignKey("users.id"), index=True)

    status = Column(String, default="pending", index=True)  # pending / approved / rejected
    current_level = Column(String, default="manager", index=True)  # manager -> admin

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")
