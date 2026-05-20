# services/comment_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comments import Comment
from app.models.task import Task


def create_comment_service(task_id: int, data, user, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 🔐 Role logic
    if data.is_internal and user.role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Employees cannot add internal comments"
        )

    comment = Comment(
        task_id=task_id,
        user_id=user.id,
        content=data.content,
        is_internal=data.is_internal
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comments_service(task_id: int, user, db: Session):
    query = db.query(Comment).filter(Comment.task_id == task_id)

    # 🔐 Hide internal comments from employees
    if user.role == "employee":
        query = query.filter(Comment.is_internal == False)

    return query.order_by(Comment.created_at.desc()).all()