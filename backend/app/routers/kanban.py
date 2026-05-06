from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import TaskStatusUpdate, TaskOut
from app.core.dependencies import get_current_user
from app.services.kanban_service import (
    update_task_status,
    get_kanban_board
)

router = APIRouter(prefix="/kanban", tags=["Kanban"])


# 🔄 UPDATE STATUS
@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
def change_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return update_task_status(task_id, payload.status, user, db)


# 📊 GET BOARD
@router.get("/board")
def get_board(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_kanban_board(user, db)