# services/notification_service.py

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.notification import Notification

from app.services.websocket_manager import manager
from app.core.logger import logger


# =====================================
# CORE FUNCTIONS
# =====================================

def create_notification(
    db: Session,
    user_id: int,
    message: str
):
    """Create a new notification"""

    notification = Notification(
        user_id=user_id,
        message=message
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    logger.info(
        f"Notification created for user {user_id}"
    )

    return notification


async def push_notification(
    user_id: int,
    message: str
):
    """Push notification via websocket"""

    try:
        await manager.send_message(
            user_id,
            message
        )

        logger.info(
            f"WebSocket notification sent to user {user_id}"
        )

    except Exception as e:
        logger.error(
            f"WebSocket error: {str(e)}"
        )


def get_unread_notifications(
    db: Session,
    user_id: int
):
    """Get unread notifications"""

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_as_read(
    db: Session,
    notification_id: int,
    user_id: int
):
    """Mark notification as read"""

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        .first()
    )

    if notification:
        notification.is_read = True
        db.commit()

        logger.info(
            f"Notification {notification_id} marked as read"
        )

    return notification


def mark_all_as_read(
    db: Session,
    user_id: int
):
    """Mark all notifications as read"""

    (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        .update({"is_read": True})
    )

    db.commit()

    logger.info(
        f"All notifications marked as read for user {user_id}"
    )


# =====================================
# ROUTER SERVICES
# =====================================

def get_notifications_service(
    db: Session,
    user
):

    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_notification_read_service(
    db: Session,
    notification_id: int,
    user
):

    notification = mark_as_read(
        db,
        notification_id,
        user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"msg": "updated"}