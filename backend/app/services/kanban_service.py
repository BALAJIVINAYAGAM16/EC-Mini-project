from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.task import TaskHistory  # if you added it


VALID_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["review"],
    "review": ["done"],
    "done": []
}


def update_task_status(task_id: int, new_status: str, user, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    current_status = task.status

    # 🔴 VALIDATION (MOST IMPORTANT)
    if new_status not in VALID_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_status} → {new_status}"
        )

    # 🔐 ROLE CHECK
    if user.role == "employee" and task.assigned_to_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # 🔄 UPDATE
    task.status = new_status
    task.updated_by = user.id

    # 🧾 OPTIONAL: HISTORY TRACKING
    try:
        history = TaskHistory(
            task_id=task.id,
            old_status=current_status,
            new_status=new_status,
            changed_by=user.id
        )
        db.add(history)
    except:
        pass  # ignore if model not present

    db.commit()
    db.refresh(task)

    return task

from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskOut


def get_kanban_board(user, db: Session):
    query = db.query(Task)

    # 🔐 ROLE FILTERING
    if user.role == "employee":
        query = query.filter(Task.assigned_to_id == user.id)

    elif user.role == "manager":
        query = query.filter(Task.created_by_id == user.id)

    tasks = query.all()

    board = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": []
    }

    for task in tasks:
        task_data = TaskOut.model_validate(task)

        board[task.status].append(task_data)

    return board