from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.approval import Approval
from app.models.approval_history import ApprovalHistory


def create_approval(data, user, db: Session):
    approval = Approval(
        title=data.title,
        description=data.description,
        requested_by=user.id
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def take_action(approval_id: int, data, user, db: Session):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(404, "Approval not found")

    # 🔐 Role-based approval logic
    if approval.current_level == "manager" and user.role != "manager":
        raise HTTPException(403, "Only manager can approve at this level")

    if approval.current_level == "admin" and user.role != "admin":
        raise HTTPException(403, "Only admin can approve at this level")

    # 🚫 Reject must have comment
    if data.action == "reject" and not data.comment:
        raise HTTPException(400, "Comment required for rejection")

    # 🔄 Logic
    if data.action == "approve":
        if approval.current_level == "manager":
            approval.current_level = "admin"  # escalate
        else:
            approval.status = "approved"

    elif data.action == "reject":
        approval.status = "rejected"

    elif data.action == "hold":
        approval.status = "pending"

    # 🧾 History
    history = ApprovalHistory(
        approval_id=approval.id,
        action_by=user.id,
        action=data.action,
        comment=data.comment
    )

    db.add(history)
    db.commit()
    db.refresh(approval)

    return approval


def get_approvals(user, db: Session):
    query = db.query(Approval)

    if user.role == "employee":
        query = query.filter(Approval.requested_by == user.id)

    return query.all()


def get_history(approval_id: int, db: Session):
    return db.query(ApprovalHistory).filter(
        ApprovalHistory.approval_id == approval_id
    ).all()