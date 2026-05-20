# routers/comment_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.routers.auth import get_current_user
from app.schemas.comments import CommentCreate, CommentOut
from app.services.comment_service import (
    create_comment_service,
    get_comments_service
)

router = APIRouter(prefix="/tasks", tags=["Comments"])


# ➕ Add comment
@router.post("/{task_id}/comments", response_model=CommentOut)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_comment_service(task_id, payload, user, db)


# 📄 Get comments
@router.get("/{task_id}/comments", response_model=List[CommentOut])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_comments_service(task_id, user, db)