from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def get_all_activity_logs(db: Session):
    return (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )


def log_activity(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    commit: bool = True,
):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    db.add(log)

    if commit:
        db.commit()
        db.refresh(log)

    return log