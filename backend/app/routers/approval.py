from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.approval import ApprovalCreate, ApprovalAction, ApprovalOut
from app.services.approval_service import (
    create_approval,
    take_action,
    get_approvals,
    get_history
)

router = APIRouter(prefix="/approvals", tags=["Approvals"])


# ➕ Create approval
@router.post("/", response_model=ApprovalOut)
def create(
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return create_approval(payload, user, db)


# 📄 Get approvals
@router.get("/", response_model=List[ApprovalOut])
def list_all(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_approvals(user, db)


# 🔄 Take action
@router.patch("/{approval_id}/action", response_model=ApprovalOut)
def action(
    approval_id: int,
    payload: ApprovalAction,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return take_action(approval_id, payload, user, db)


# 📜 History
@router.get("/{approval_id}/history")
def history(
    approval_id: int,
    db: Session = Depends(get_db)
):
    return get_history(approval_id, db)