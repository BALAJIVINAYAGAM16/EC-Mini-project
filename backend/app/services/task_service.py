from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
 
from app.models.activity_log import ActivityLog
from app.models.audit import AuditLog
from app.models.task import Task, TaskHistory
from app.models.user import User
 
WORKFLOW_STATUSES = ("todo", "in_progress", "review", "done")
ALLOWED_TRANSITIONS = {
    "todo": ("in_progress",),
    "in_progress": ("review",),
    "review": ("done",),
    "done": (),
}
 
 
def normalize_status(value: str) -> str:
    status_value = getattr(value, "value", value)
    status_value = str(status_value).strip().lower()
    if status_value not in WORKFLOW_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported task status: {status_value}",
        )
    return status_value
 
 
def validate_status_transition(current_status: str, new_status: str) -> str:
    current = normalize_status(current_status)
    new = normalize_status(new_status)
 
    if current == new:
        return new
 
    if new not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition: {current} -> {new}",
        )
    return new
 
 
def can_access_task(task: Task, user: User) -> bool:
    if user.role == "admin":
        return True
    if user.role == "manager":
        return task.created_by_id == user.id or task.assigned_to_id == user.id
    return task.assigned_to_id == user.id
 
 
def apply_task_status(task: Task, new_status: str, user: User, db: Session) -> Task:
    status_value = validate_status_transition(task.status, new_status)
 
    if not can_access_task(task, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
 
    if task.status != status_value:
        db.add(
            TaskHistory(
                task_id=task.id,
                old_status=task.status,
                new_status=status_value,
                changed_by=user.id,
            )
        )
        task.status = status_value
        task.updated_by = user.id
        db.add(
            ActivityLog(
                user_id=user.id,
                action="TASK_STATUS_UPDATED",
                entity_type="TASK",
                entity_id=task.id,
            )
        )
        db.add(AuditLog(user_id=user.id, action="TASK_STATUS_UPDATED", entity="TASK", entity_id=task.id))
 
    return task
 
 
def visible_tasks_query(db: Session, user: User):
    query = db.query(Task)
    if user.role == "admin":
        return query
    if user.role == "manager":
        return query.filter(or_(Task.created_by_id == user.id, Task.assigned_to_id == user.id))
    return query.filter(Task.assigned_to_id == user.id)
 
 
def get_kanban_board(user: User, db: Session):
    board = {status_name: [] for status_name in WORKFLOW_STATUSES}
    tasks = (
        visible_tasks_query(db, user)
        .options(joinedload(Task.assigned_to))
        .order_by(Task.updated_at.desc())
        .all()
    )
    for task in tasks:
        board.setdefault(task.status, []).append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "created_by_id": task.created_by_id,
                "assigned_to_id": task.assigned_to_id,
                "assigned_to_name": task.assigned_to.name if task.assigned_to else None,
                "updated_by": task.updated_by,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            }
        )
    return board