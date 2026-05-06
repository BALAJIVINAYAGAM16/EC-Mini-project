from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.task import Task


def _task_query_for_user(user, db: Session):
    query = db.query(Task)

    if user.role == "employee":
        return query.filter(Task.assigned_to_id == user.id)

    if user.role == "manager":
        return query.filter(Task.created_by_id == user.id)

    return query


def get_dashboard_summary(user, db: Session):
    task_query = _task_query_for_user(user, db)
    total_tasks = task_query.count()

    status_counts = {
        status: count
        for status, count in task_query.with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    }

    completed = status_counts.get("done", 0)
    approval_query = db.query(Approval)
    if user.role == "employee":
        approval_query = approval_query.filter(Approval.requested_by == user.id)

    return {
        "total_tasks": total_tasks,
        "status_distribution": status_counts,
        "pending_tasks": total_tasks - completed,
        "completed_tasks": completed,
        "pending_approvals": approval_query.filter(Approval.status == "pending").count(),
    }


def get_task_distribution(user, db: Session):
    data = (
        _task_query_for_user(user, db)
        .with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )

    return [{"status": status, "count": count} for status, count in data]


def get_approval_stats(db: Session):
    data = (
        db.query(Approval.status, func.count(Approval.id))
        .group_by(Approval.status)
        .all()
    )

    return {status: count for status, count in data}
