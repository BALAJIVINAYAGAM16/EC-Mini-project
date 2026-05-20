import anyio

from app.services.websocket_manager import manager


def notify_kanban_changed(task_id: int):
    try:
        anyio.from_thread.run(
            manager.broadcast_json,
            {"type": "kanban.updated", "task_id": task_id},
        )
    except RuntimeError:
        pass
