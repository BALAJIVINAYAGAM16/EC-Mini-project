from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.approval_history import ApprovalHistory

from app.services.audit_service import log_action


def create_approval_service(data, user, db: Session):

    approval = Approval(
        title=data.title,
        description=data.description,
        requested_by=user.id,
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    log_action(
        db,
        user.id,
        "create_approval",
        "approval",
        approval.id,
    )

    return approval


def take_action_service(
    approval_id: int,
    data,
    user,
    db: Session,
):

    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(404, "Approval not found")

    action = data.action.lower()

    if action not in {"approve", "reject", "hold"}:
        raise HTTPException(400, "Invalid approval action")

    if approval.status in {"approved", "rejected"}:
        raise HTTPException(
            400,
            "Approval already finalized",
        )

    if (
        approval.current_level == "manager"
        and user.role != "manager"
    ):
        raise HTTPException(
            403,
            "Only manager can approve at this level",
        )

    if (
        approval.current_level == "admin"
        and user.role != "admin"
    ):
        raise HTTPException(
            403,
            "Only admin can approve at this level",
        )

    if action == "reject" and not data.comment:
        raise HTTPException(
            400,
            "Comment required for rejection",
        )

    if action == "approve":

        if approval.current_level == "manager":
            approval.current_level = "admin"
        else:
            approval.status = "approved"

    elif action == "reject":
        approval.status = "rejected"

    elif action == "hold":
        approval.status = "pending"

    history = ApprovalHistory(
        approval_id=approval.id,
        action_by=user.id,
        action=action,
        comment=data.comment,
    )

    db.add(history)

    db.commit()
    db.refresh(approval)

    log_action(
        db,
        user.id,
        f"approval_{action}",
        "approval",
        approval.id,
    )

    return approval


def get_approvals_service(user, db: Session):

    query = db.query(Approval)

    if user.role == "employee":
        query = query.filter(
            Approval.requested_by == user.id
        )

    return (
        query.order_by(
            Approval.created_at.desc()
        ).all()
    )


def get_history_service(
    approval_id: int,
    db: Session,
):

    return (
        db.query(ApprovalHistory)
        .filter(
            ApprovalHistory.approval_id == approval_id
        )
        .order_by(
            ApprovalHistory.created_at.desc()
        )
        .all()
    )