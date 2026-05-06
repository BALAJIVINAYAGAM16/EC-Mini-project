from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime
from app.db.database import Base

class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id = Column(Integer, primary_key=True)
    approval_id = Column(Integer, ForeignKey("approvals.id"))

    action_by = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # approve / reject / hold
    comment = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)