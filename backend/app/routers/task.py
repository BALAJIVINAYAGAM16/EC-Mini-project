from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.task import Task
from app.schemas.task import TaskAssign, TaskCreate, TaskUpdate
from app.core.dependencies import get_current_user, require_role
router = APIRouter(prefix="/tasks", tags=["tasks"])
 
 
@router.post("/")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user = Depends(require_role(["admin", "manager"]))
):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_by_id=user["user_id"]
    )
 
    # ✅ Only assign if provided and not 0
    if task.assigned_to_id and task.assigned_to_id != 0:
        new_task.assigned_to_id = task.assigned_to_id
 
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
 
    return new_task
 
@router.patch("/{task_id}/assign")
def assign_task(
    task_id: int,
    assignment: TaskAssign,
    db: Session = Depends(get_db),
    user = Depends(require_role(["admin", "manager"]))
):
    task = db.query(Task).filter(Task.id == task_id).first()
 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    task.assigned_to_id = assignment.assigned_to_id
    db.commit()
 
    return {"message": "Task assigned"}
 
@router.get("/")
def get_tasks(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user["role"] == "admin":
        return db.query(Task).all()
 
    elif user["role"] == "manager":
        return db.query(Task).filter(
            Task.created_by_id == user["user_id"]
        ).all()
 
    else:  # employee
        return db.query(Task).filter(
            Task.assigned_to_id == user["user_id"]
        ).all()
       
@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    return task
 
@router.put("/{task_id}")
def update_task(
    task_id: int,
    updated: TaskUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_role(["admin", "manager"]))
):
    task = db.query(Task).filter(Task.id == task_id).first()
 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(task, key, value)
 
    db.commit()
    db.refresh(task)
 
    return task
 
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    task = db.query(Task).filter(Task.id == task_id).first()
 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    db.delete(task)
    db.commit()
 
    return {"message": "Task deleted"}
 
 