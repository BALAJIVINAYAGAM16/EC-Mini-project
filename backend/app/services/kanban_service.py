# services/kanban_service.py

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.models.task import (
    Task,
    TaskHistory
)
from app.schemas.task import TaskOut

from app.services.realtime_service import (
    notify_kanban_changed
)


VALID_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["review"],
    "review": ["done"],
    "done": [],
}


# =====================================
# CORE FUNCTIONS
# =====================================

def update_task_status(
    task_id: int,
    new_status: str,
    user,
    db: Session
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    current_status = task.status

    if new_status not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task status: {new_status}",
        )

    if new_status not in VALID_TRANSITIONS.get(
        current_status,
        []
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition: {current_status} -> {new_status}",
        )

    if (
        user.role == "employee"
        and task.assigned_to_id != user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only update assigned tasks",
        )

    if (
        user.role == "manager"
        and task.created_by_id != user.id
        and task.assigned_to_id != user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only update tasks they created or own",
        )

    task.status = new_status
    task.updated_by = user.id

    db.add(
        TaskHistory(
            task_id=task.id,
            old_status=current_status,
            new_status=new_status,
            changed_by=user.id,
        )
    )

    db.commit()
    db.refresh(task)

    cache.delete_prefix("kanban:")
    cache.delete_prefix("dashboard:")

    notify_kanban_changed(task.id)

    return task


def get_kanban_board(
    user,
    db: Session
):

    query = db.query(Task)

    if user.role == "employee":
        query = query.filter(
            Task.assigned_to_id == user.id
        )

    elif user.role == "manager":
        query = query.filter(
            or_(
                Task.created_by_id == user.id,
                Task.assigned_to_id == user.id
            )
        )

    board = {
        status: []
        for status in VALID_TRANSITIONS
    }

    tasks = (
        query.order_by(Task.updated_at.desc())
        .all()
    )

    for task in tasks:
        board.setdefault(
            task.status,
            []
        ).append(
            TaskOut.model_validate(task)
        )

    return board


# =====================================
# ROUTER SERVICES
# =====================================

def update_task_status_service(
    task_id: int,
    new_status: str,
    user,
    db: Session
):
    return update_task_status(
        task_id,
        new_status,
        user,
        db
    )


def get_kanban_board_service(
    user,
    db: Session
):
    return get_kanban_board(
        user,
        db
    )