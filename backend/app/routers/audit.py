from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit-logs", tags=["Audit"])

@router.get("/")
def get_logs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(AuditLog)
    if user.role != "admin":
        query = query.filter(AuditLog.user_id == user.id)
    return query.order_by(AuditLog.timestamp.desc()).all()
