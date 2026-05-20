from datetime import datetime
from sqlalchemy import func

from app.models.task import Task
from app.models.user import User

def generate_ai_summary(tasks):
    now = datetime.utcnow()
    pending = [t for t in tasks if t.status != "done"]
    high_priority = [t for t in pending if t.priority == "high"]
    delayed = [t for t in pending if t.due_date and t.due_date < now]

    return {
        "pending_tasks": len(pending),
        "high_priority_tasks": len(high_priority),
        "delayed_tasks": len(delayed),
        "delay_risks": [
            {"id": t.id, "title": t.title, "due_date": t.due_date, "priority": t.priority}
            for t in pending
            if t.priority == "high" or (t.due_date and t.due_date < now)
        ][:10],
        "ai_summary": f"{len(high_priority)} high priority tasks pending; {len(delayed)} delayed tasks"
    }


def recommend_assignee(db):
    workload = dict(
        db.query(Task.assigned_to_id, func.count(Task.id))
        .filter(Task.assigned_to_id.isnot(None), Task.status != "done")
        .group_by(Task.assigned_to_id)
        .all()
    )
    completed = dict(
        db.query(Task.assigned_to_id, func.count(Task.id))
        .filter(Task.assigned_to_id.isnot(None), Task.status == "done")
        .group_by(Task.assigned_to_id)
        .all()
    )
    users = db.query(User).filter(User.is_active.is_(True), User.role.in_(["employee", "manager"])).all()
    ranked = sorted(
        users,
        key=lambda user: (
            workload.get(user.id, 0),
            -completed.get(user.id, 0),
            user.name.lower(),
        ),
    )
    return [
        {
            "user_id": user.id,
            "name": user.name,
            "role": user.role,
            "open_tasks": workload.get(user.id, 0),
            "completed_tasks": completed.get(user.id, 0),
        }
        for user in ranked[:5]
    ]
