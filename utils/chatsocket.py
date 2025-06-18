from fastapi import WebSocket
from typing import Callable, Awaitable

class ChatSocket:
    def __init__(self):
        # You can add state here if needed (e.g., connected clients, status updates)
        pass

    async def handle(self, websocket: WebSocket):
        # Accept the WebSocket connection
        await websocket.accept()
        try:
            while True:
                # Wait for a message from the client
                data = await websocket.receive_text()
                # Echo the message back to the client
                await websocket.send_text(f"Echo: {data}")
        except Exception as e:
            # Handle disconnects or errors
            await websocket.close() 

async def on_message(message: str):
    print(f"Received message: {message}")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def handler(self, websocket: WebSocket, on_message: Callable[[str], Awaitable[None]] = on_message):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await on_message(data)
        except Exception as e:
            await websocket.close()
        finally:
            self.disconnect(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)