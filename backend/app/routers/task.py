# routers/task_router.py

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_role
)

from app.db.database import get_db

from app.models.user import User

from app.schemas.task import (
    TaskAssign,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    TaskStatusUpdate
)

from app.services.task_service import (
    create_task_service,
    get_tasks_service,
    get_kanban_service,
    get_task_service,
    patch_task_status_service,
    update_task_service,
    delete_task_service,
    assign_task_service,
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post(
    "/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "manager"])
    ),
):
    return create_task_service(
        task,
        db,
        current_user
    )


@router.get("/", response_model=list[TaskOut])
def get_tasks(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tasks_service(
        response,
        skip,
        limit,
        db,
        current_user
    )


@router.get("/kanban")
def get_kanban(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_kanban_service(
        current_user,
        db
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_service(
        task_id,
        db,
        current_user
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskOut
)
def patch_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return patch_task_status_service(
        task_id,
        payload,
        db,
        current_user
    )


@router.put(
    "/{task_id}",
    response_model=TaskOut
)
def update_task(
    task_id: int,
    updated: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_task_service(
        task_id,
        updated,
        db,
        current_user
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin"])
    ),
):
    return delete_task_service(
        task_id,
        db,
        current_user
    )


@router.patch(
    "/{task_id}/assign",
    response_model=TaskOut
)
def assign_task(
    task_id: int,
    assignment: TaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "manager"])
    ),
):
    return assign_task_service(
        task_id,
        assignment,
        db,
        current_user
    )