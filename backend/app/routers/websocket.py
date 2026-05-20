# routers/websocket_router.py

from fastapi import (
    APIRouter,
    WebSocket
)

from app.services.websocket_manager import (
    websocket_connection_service
)

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int
):
    await websocket_connection_service(
        websocket,
        user_id
    )
