# services/audit_service.py

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def get_audit_logs(db: Session, user):
    query = db.query(AuditLog)

    if user.role != "admin":
        query = query.filter(AuditLog.user_id == user.id)

    return query.order_by(AuditLog.timestamp.desc()).all()


def log_action(db: Session, user_id, action, entity, entity_id):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id
    )

    db.add(log)
    db.commit()