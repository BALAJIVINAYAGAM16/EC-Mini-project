from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskAssign, TaskCreate, TaskOut, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _ensure_user_exists(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
    return user


def _can_access_task(task: Task, current_user: User):
    if current_user.role == "admin":
        return True
    if current_user.role == "manager":
        return task.created_by_id == current_user.id or task.assigned_to_id == current_user.id
    return task.assigned_to_id == current_user.id


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    if task.assigned_to_id:
        _ensure_user_exists(db, task.assigned_to_id)

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority.value,
        due_date=task.due_date,
        created_by_id=current_user.id,
        assigned_to_id=task.assigned_to_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=list[TaskOut])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return db.query(Task).order_by(Task.created_at.desc()).all()
    if current_user.role == "manager":
        return (
            db.query(Task)
            .filter(or_(Task.created_by_id == current_user.id, Task.assigned_to_id == current_user.id))
            .order_by(Task.created_at.desc())
            .all()
        )
    return (
        db.query(Task)
        .filter(Task.assigned_to_id == current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_task_or_404(db, task_id)
    if not _can_access_task(task, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updated: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_task_or_404(db, task_id)
    changes = updated.model_dump(exclude_unset=True)

    if current_user.role == "employee":
        if task.assigned_to_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only update assigned tasks")
        disallowed = set(changes) - {"status"}
        if disallowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only update task status")
    elif current_user.role == "manager" and task.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only update their own tasks")

    if "assigned_to_id" in changes and changes["assigned_to_id"] is not None:
        _ensure_user_exists(db, changes["assigned_to_id"])

    for key, value in changes.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(task, key, value)
    task.updated_by = current_user.id

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"])),
):
    task = _get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


@router.patch("/{task_id}/assign", response_model=TaskOut)
def assign_task(
    task_id: int,
    assignment: TaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    task = _get_task_or_404(db, task_id)
    if current_user.role == "manager" and task.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only assign their own tasks")

    _ensure_user_exists(db, assignment.assigned_to_id)
    task.assigned_to_id = assignment.assigned_to_id
    task.updated_by = current_user.id
    db.commit()
    db.refresh(task)
    return task
