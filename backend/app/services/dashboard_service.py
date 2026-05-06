from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task
from app.models.approval import Approval


# 📊 SUMMARY
def get_dashboard_summary(user, db: Session):
    query = db.query(Task)

    # 🔐 Role filtering
    if user.role == "employee":
        query = query.filter(Task.assigned_to_id == user.id)

    elif user.role == "manager":
        query = query.filter(Task.created_by_id == user.id)

    total_tasks = query.count()

    # Count by status
    status_counts = {
    status: count
    for status, count in (
        db.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
}
    completed = status_counts.get("done", 0)

    # Pending approvals
    pending_approvals = db.query(Approval).filter(
        Approval.status == "pending"
    ).count()

    return {
        "total_tasks": total_tasks,
        "status_distribution": status_counts,
        "completed_tasks": completed,
        "pending_approvals": pending_approvals
    }


# 📈 TASK DISTRIBUTION
def get_task_distribution(user, db: Session):
    query = db.query(Task)

    if user.role == "employee":
        query = query.filter(Task.assigned_to_id == user.id)

    elif user.role == "manager":
        query = query.filter(Task.created_by_id == user.id)

    data = (
        db.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )

    return [{"status": status, "count": count} for status, count in data]


# 📋 APPROVAL STATS
def get_approval_stats(db: Session):
    data = (
        db.query(Approval.status, func.count(Approval.id))
        .group_by(Approval.status)
        .all()
    )

    return [{"status": status, "count": count} for status, count in data]