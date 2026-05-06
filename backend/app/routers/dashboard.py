from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.services.dashboard_service import (
    get_dashboard_summary,
    get_task_distribution,
    get_approval_stats
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# 📊 Summary
@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_dashboard_summary(user, db)


# 📈 Task distribution
@router.get("/task-distribution")
def task_distribution(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_task_distribution(user, db)


# 📋 Approval stats
@router.get("/approvals")
def approvals(
    db: Session = Depends(get_db)
):
    return get_approval_stats(db)