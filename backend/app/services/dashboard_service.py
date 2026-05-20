# services/dashboard_service.py

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.models.approval import Approval
from app.models.task import Task
from app.services.ai_service import (
    generate_ai_summary,
    recommend_assignee
)
from app.services.task_service import (
    WORKFLOW_STATUSES,
    visible_tasks_query
)


def _visible_tasks(user, db: Session):
    return visible_tasks_query(db, user)


def get_dashboard_summary(user, db: Session):
    query = _visible_tasks(user, db)

    total_tasks = query.count()

    grouped = (
        query.with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )

    status_counts = {
        status_name: 0
        for status_name in WORKFLOW_STATUSES
    }

    status_counts.update({
        status_name: count
        for status_name, count in grouped
    })

    approval_query = db.query(Approval).filter(
        Approval.status == "pending"
    )

    if user.role == "employee":
        approval_query = approval_query.filter(
            Approval.requested_by == user.id
        )

    tasks = query.all()

    return {
        "total_tasks": total_tasks,
        "tasks_by_status": status_counts,
        "status_distribution": status_counts,
        "completed_tasks": status_counts.get("done", 0),
        "pending_approvals": approval_query.count(),
        **generate_ai_summary(tasks),
    }


def get_task_distribution(user, db: Session):
    data = (
        _visible_tasks(user, db)
        .with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )

    counts = {
        status_name: 0
        for status_name in WORKFLOW_STATUSES
    }

    counts.update({
        status_name: count
        for status_name, count in data
    })

    return [
        {"status": status_name, "count": count}
        for status_name, count in counts.items()
    ]


def get_approval_stats(user, db: Session):
    query = db.query(Approval)

    if user.role == "employee":
        query = query.filter(
            Approval.requested_by == user.id
        )

    data = (
        query.with_entities(
            Approval.status,
            func.count(Approval.id)
        )
        .group_by(Approval.status)
        .all()
    )

    counts = {
        "approved": 0,
        "rejected": 0,
        "pending": 0
    }

    counts.update({
        status_name: count
        for status_name, count in data
    })

    return counts


# =========================
# SERVICE FUNCTIONS
# =========================

def get_summary_service(user, db: Session):
    cache_key = f"dashboard:summary:{user.id}:{user.role}"

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    data = get_dashboard_summary(user, db)

    cache.set(cache_key, data, ttl_seconds=30)

    return data


def get_task_distribution_service(user, db: Session):
    return get_task_distribution(user, db)


def get_approval_stats_service(user, db: Session):
    return get_approval_stats(user, db)


def get_ai_summary_service(user, db: Session):
    tasks = visible_tasks_query(db, user).all()

    return generate_ai_summary(tasks)


def get_manager_dashboard_service(user, db: Session):
    return {
        **get_dashboard_summary(user, db),
        "approval_stats": get_approval_stats(user, db),
        "assignment_recommendations": recommend_assignee(db),
    }


def get_admin_dashboard_service(user, db: Session):
    return {
        **get_dashboard_summary(user, db),
        "approval_stats": get_approval_stats(user, db),
        "task_distribution": get_task_distribution(user, db),
        "assignment_recommendations": recommend_assignee(db),
    }