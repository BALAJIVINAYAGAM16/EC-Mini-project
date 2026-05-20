# routers/audit_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.services.audit_service import get_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("/")
def get_logs(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_audit_logs(db, user)