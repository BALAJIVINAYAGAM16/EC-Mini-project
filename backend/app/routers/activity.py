from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("/")
def get_activity_logs(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "manager"])),
):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).all()
