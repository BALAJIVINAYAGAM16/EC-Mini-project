from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.approval import (
    ApprovalCreate,
    ApprovalAction,
    ApprovalHistoryOut,
    ApprovalOut,
)

from app.services.approval_service import (
    create_approval_service,
    take_action_service,
    get_approvals_service,
    get_history_service,
)

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


@router.post("/", response_model=ApprovalOut)
def create_approval(
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return create_approval_service(payload, user, db)


@router.get("/", response_model=List[ApprovalOut])
def get_approvals(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_approvals_service(user, db)


@router.patch("/{approval_id}/action", response_model=ApprovalOut)
def take_action(
    approval_id: int,
    payload: ApprovalAction,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return take_action_service(
        approval_id,
        payload,
        user,
        db,
    )


@router.get(
    "/{approval_id}/history",
    response_model=List[ApprovalHistoryOut],
)
def get_history(
    approval_id: int,
    db: Session = Depends(get_db),
):
    return get_history_service(approval_id, db)