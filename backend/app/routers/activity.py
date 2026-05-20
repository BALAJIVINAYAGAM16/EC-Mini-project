from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.user import User
from app.services.activity_service import get_all_activity_logs

router = APIRouter(
    prefix="/activity",
    tags=["Activity"]
)


@router.get("/")
def get_activity(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "manager"])),
):
    return get_all_activity_logs(db)