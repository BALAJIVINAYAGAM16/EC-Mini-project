# services/websocket_service.py

import json

from fastapi import (
    WebSocket,
    WebSocketDisconnect
)


class ConnectionManager:

    def __init__(self):

        self.active_connections = {}


    async def connect(
        self,
        user_id: int,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.active_connections[user_id] = websocket


    def disconnect(
        self,
        user_id: int
    ):

        self.active_connections.pop(
            user_id,
            None
        )


    async def send_personal_message(
        self,
        user_id: int,
        message: str
    ):

        websocket = self.active_connections.get(
            user_id
        )

        if websocket:
            await websocket.send_text(message)


    async def send_message(
        self,
        user_id: int,
        message: str
    ):

        await self.send_personal_message(
            user_id,
            message
        )


    async def broadcast_json(
        self,
        payload: dict
    ):

        stale_users = []

        message = json.dumps(
            payload,
            default=str
        )

        for user_id, websocket in self.active_connections.items():

            try:
                await websocket.send_text(message)

            except Exception:
                stale_users.append(user_id)

        for user_id in stale_users:
            self.disconnect(user_id)


manager = ConnectionManager()


# =====================================
# ROUTER SERVICES
# =====================================

async def websocket_connection_service(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(user_id)