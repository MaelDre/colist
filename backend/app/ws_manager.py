import json

from starlette.websockets import WebSocket

from app.state import store


class ConnectionManager:
    async def connect(self, list_id: str, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        state = store.get(list_id)
        is_new_session = not state.connections.get(session_id)
        state.connections.setdefault(session_id, set()).add(websocket)
        if is_new_session:
            await self.broadcast(
                list_id,
                {"type": "presence_join", "session_id": session_id, "color": state.color_for(session_id)},
            )

    async def disconnect(self, list_id: str, session_id: str, websocket: WebSocket) -> None:
        state = store.get(list_id)
        conns = state.connections.get(session_id)
        if not conns:
            return
        conns.discard(websocket)
        if not conns:
            state.connections.pop(session_id, None)
            await self.broadcast(list_id, {"type": "presence_leave", "session_id": session_id})

    async def broadcast(self, list_id: str, message: dict) -> None:
        state = store.get(list_id)
        payload = json.dumps(message, default=str)
        dead: list[tuple[str, WebSocket]] = []
        for session_id, conns in list(state.connections.items()):
            for ws in list(conns):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead.append((session_id, ws))
        for session_id, ws in dead:
            conns = state.connections.get(session_id)
            if conns:
                conns.discard(ws)
                if not conns:
                    state.connections.pop(session_id, None)


manager = ConnectionManager()
