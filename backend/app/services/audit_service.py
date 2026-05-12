from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_action(db: Session, user_id, action, entity, entity_id):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id
    )
    db.add(log)
    db.commit()