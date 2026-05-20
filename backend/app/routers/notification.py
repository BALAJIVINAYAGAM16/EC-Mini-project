# routers/notification_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db

from app.services.notification_service import (
    get_notifications_service,
    mark_notification_read_service,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_notifications_service(
        db,
        user
    )


@router.patch("/{id}/read")
def mark_read(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return mark_notification_read_service(
        db,
        id,
        user
    )