from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()

        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(
        self,
        user_id: int,
        message: str
    ):

        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_text(message)

    async def send_message(self, user_id: int, message: str):
        await self.send_personal_message(user_id, message)

manager = ConnectionManager()
