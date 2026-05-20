# routers/dashboard_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.services.dashboard_service import (
    get_summary_service,
    get_task_distribution_service,
    get_approval_stats_service,
    get_ai_summary_service,
    get_manager_dashboard_service,
    get_admin_dashboard_service
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_summary_service(user, db)


@router.get("/task-distribution")
def task_distribution(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_task_distribution_service(user, db)


@router.get("/approvals")
def approvals(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_approval_stats_service(user, db)


@router.get("/ai-summary")
def ai_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_ai_summary_service(user, db)


@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role(["employee"]))
):
    return get_summary_service(user, db)


@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role(["manager"]))
):
    return get_manager_dashboard_service(user, db)


@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"]))
):
    return get_admin_dashboard_service(user, db)