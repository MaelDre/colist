from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app import models
from app.database import SessionLocal
from app.session import cookie_name
from app.state import new_session_id, store
from app.ws_manager import manager

router = APIRouter()


@router.websocket("/api/lists/{list_id}/ws")
async def list_ws(websocket: WebSocket, list_id: str):
    db = SessionLocal()
    try:
        db_list = db.get(models.List, list_id)
    finally:
        db.close()

    if db_list is None:
        await websocket.close(code=4404)
        return

    session_id = websocket.cookies.get(cookie_name(list_id)) or new_session_id()
    store.get(list_id).color_for(session_id)

    await manager.connect(list_id, session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(list_id, session_id, websocket)
