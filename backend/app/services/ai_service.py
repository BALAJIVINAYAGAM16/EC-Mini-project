from datetime import datetime

def generate_ai_summary(tasks):
    now = datetime.utcnow()
    pending = [t for t in tasks if t.status != "done"]
    high_priority = [t for t in pending if t.priority == "high"]
    delayed = [t for t in pending if t.due_date and t.due_date < now]

    return {
        "pending_tasks": len(pending),
        "high_priority_tasks": len(high_priority),
        "delayed_tasks": len(delayed),
        "ai_summary": f"{len(high_priority)} high priority tasks pending; {len(delayed)} delayed tasks"
    }
