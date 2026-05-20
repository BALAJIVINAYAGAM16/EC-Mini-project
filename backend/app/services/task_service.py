# services/task_service.py

from fastapi import (
    HTTPException,
    Response,
    status
)

from sqlalchemy import or_
from sqlalchemy.orm import (
    Session,
    joinedload
)

from app.core.cache import cache

from app.models.activity_log import ActivityLog
from app.models.audit import AuditLog

from app.models.task import (
    Task,
    TaskHistory
)

from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskAssign,
    TaskStatusUpdate
)

from app.services.realtime_service import (
    notify_kanban_changed
)


WORKFLOW_STATUSES = (
    "todo",
    "in_progress",
    "review",
    "done"
)

ALLOWED_TRANSITIONS = {
    "todo": ("in_progress",),
    "in_progress": ("review",),
    "review": ("done",),
    "done": (),
}


# =====================================
# HELPERS
# =====================================

def get_task_or_404(
    db: Session,
    task_id: int
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


def ensure_user_exists(
    db: Session,
    user_id: int
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    return user


def can_access_task(
    task: Task,
    user: User
):

    if user.role == "admin":
        return True

    if user.role == "manager":
        return (
            task.created_by_id == user.id
            or task.assigned_to_id == user.id
        )

    return task.assigned_to_id == user.id


def normalize_status(value: str):

    status_value = getattr(
        value,
        "value",
        value
    )

    status_value = (
        str(status_value)
        .strip()
        .lower()
    )

    if status_value not in WORKFLOW_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported task status: {status_value}",
        )

    return status_value


def validate_status_transition(
    current_status: str,
    new_status: str
):

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


def apply_task_status(
    task: Task,
    new_status: str,
    user: User,
    db: Session
):

    status_value = validate_status_transition(
        task.status,
        new_status
    )

    if not can_access_task(task, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

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

        db.add(
            AuditLog(
                user_id=user.id,
                action="TASK_STATUS_UPDATED",
                entity="TASK",
                entity_id=task.id
            )
        )

    return task


def visible_tasks_query(
    db: Session,
    user: User
):

    query = db.query(Task)

    if user.role == "admin":
        return query

    if user.role == "manager":
        return query.filter(
            or_(
                Task.created_by_id == user.id,
                Task.assigned_to_id == user.id
            )
        )

    return query.filter(
        Task.assigned_to_id == user.id
    )


def clear_task_cache():
    cache.delete_prefix("kanban:")
    cache.delete_prefix("dashboard:")


# =====================================
# CORE FUNCTIONS
# =====================================

def get_kanban_board(
    user: User,
    db: Session
):

    board = {
        status_name: []
        for status_name in WORKFLOW_STATUSES
    }

    tasks = (
        visible_tasks_query(db, user)
        .options(joinedload(Task.assigned_to))
        .order_by(Task.updated_at.desc())
        .all()
    )

    for task in tasks:

        board.setdefault(
            task.status,
            []
        ).append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_by_id": task.created_by_id,
            "assigned_to_id": task.assigned_to_id,
            "assigned_to_name": (
                task.assigned_to.name
                if task.assigned_to
                else None
            ),
            "updated_by": task.updated_by,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        })

    return board


# =====================================
# ROUTER SERVICES
# =====================================

def create_task_service(
    task: TaskCreate,
    db: Session,
    current_user: User
):

    if task.assigned_to_id:
        ensure_user_exists(
            db,
            task.assigned_to_id
        )

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

    clear_task_cache()

    notify_kanban_changed(new_task.id)

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="create",
            entity="task",
            entity_id=new_task.id
        )
    )

    db.commit()

    return new_task


def get_tasks_service(
    response: Response,
    skip: int,
    limit: int,
    db: Session,
    current_user: User
):

    query = (
        db.query(Task)
        .options(joinedload(Task.assigned_to))
    )

    visible_query = visible_tasks_query(
        db,
        current_user
    )

    response.headers["X-Total-Count"] = str(
        visible_query.count()
    )

    return (
        visible_query
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_kanban_service(
    current_user: User,
    db: Session
):

    cache_key = (
        f"kanban:{current_user.id}:{current_user.role}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    board = get_kanban_board(
        current_user,
        db
    )

    cache.set(
        cache_key,
        board,
        ttl_seconds=30
    )

    return board


def get_task_service(
    task_id: int,
    db: Session,
    current_user: User
):

    task = get_task_or_404(
        db,
        task_id
    )

    if not can_access_task(
        task,
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return task


def patch_task_status_service(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session,
    current_user: User
):

    task = get_task_or_404(
        db,
        task_id
    )

    apply_task_status(
        task,
        payload.status.value,
        current_user,
        db
    )

    db.commit()
    db.refresh(task)

    clear_task_cache()

    notify_kanban_changed(task.id)

    return task


def update_task_service(
    task_id: int,
    updated: TaskUpdate,
    db: Session,
    current_user: User
):

    task = get_task_or_404(
        db,
        task_id
    )

    changes = updated.model_dump(
        exclude_unset=True
    )

    if current_user.role == "employee":

        if task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employees can only update assigned tasks"
            )

        disallowed = set(changes) - {"status"}

        if disallowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employees can only update task status"
            )

    elif (
        current_user.role == "manager"
        and task.created_by_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only update their own tasks"
        )

    if (
        "assigned_to_id" in changes
        and changes["assigned_to_id"] is not None
    ):
        ensure_user_exists(
            db,
            changes["assigned_to_id"]
        )

    if "status" in changes:

        status_value = changes["status"].value

        if status_value != task.status:

            apply_task_status(
                task,
                status_value,
                current_user,
                db
            )

    for key, value in changes.items():

        if hasattr(value, "value"):
            value = value.value

        setattr(task, key, value)

    task.updated_by = current_user.id

    db.commit()
    db.refresh(task)

    clear_task_cache()

    notify_kanban_changed(task.id)

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="update",
            entity="task",
            entity_id=task.id
        )
    )

    db.commit()

    return task


def delete_task_service(
    task_id: int,
    db: Session,
    current_user: User
):

    task = get_task_or_404(
        db,
        task_id
    )

    db.delete(task)
    db.commit()

    clear_task_cache()

    notify_kanban_changed(task_id)

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="delete",
            entity="task",
            entity_id=task_id
        )
    )

    db.commit()

    return {
        "message": "Task deleted"
    }


def assign_task_service(
    task_id: int,
    assignment: TaskAssign,
    db: Session,
    current_user: User
):

    task = get_task_or_404(
        db,
        task_id
    )

    if (
        current_user.role == "manager"
        and task.created_by_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only assign their own tasks"
        )

    ensure_user_exists(
        db,
        assignment.assigned_to_id
    )

    task.assigned_to_id = assignment.assigned_to_id
    task.updated_by = current_user.id

    db.commit()
    db.refresh(task)

    clear_task_cache()

    notify_kanban_changed(task.id)

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="assign",
            entity="task",
            entity_id=task.id
        )
    )

    db.commit()

    return task