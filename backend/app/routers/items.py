from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.session import get_or_create_session
from app.state import store
from app.ws_manager import manager

router = APIRouter(prefix="/api/lists/{list_id}/items", tags=["items"])


def _get_list_or_404(db: Session, list_id: str) -> models.List:
    db_list = db.get(models.List, list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list


@router.post("", response_model=schemas.ItemOut, status_code=201)
async def add_item(
    list_id: str,
    payload: schemas.ItemCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _get_list_or_404(db, list_id)
    session_id = get_or_create_session(list_id, request, response)
    color = store.get(list_id).color_for(session_id)

    item = models.Item(
        list_id=list_id,
        name=payload.name,
        last_edited_by_color=color,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    item_out = schemas.ItemOut.model_validate(item)
    await manager.broadcast(list_id, {"type": "item_added", "item": item_out.model_dump(mode="json")})
    return item_out


@router.patch("/{item_id}", response_model=schemas.ItemOut)
async def edit_item(
    list_id: str,
    item_id: str,
    payload: schemas.ItemUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _get_list_or_404(db, list_id)
    item = db.get(models.Item, item_id)
    if item is None or item.list_id != list_id:
        raise HTTPException(status_code=404, detail="Item not found")

    session_id = get_or_create_session(list_id, request, response)
    color = store.get(list_id).color_for(session_id)

    if payload.name is not None:
        item.name = payload.name
    item.last_edited_by_color = color
    item.last_edited_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    item_out = schemas.ItemOut.model_validate(item)
    await manager.broadcast(list_id, {"type": "item_edited", "item": item_out.model_dump(mode="json")})
    return item_out


@router.delete("/{item_id}", status_code=204)
async def remove_item(list_id: str, item_id: str, db: Session = Depends(get_db)):
    _get_list_or_404(db, list_id)
    item = db.get(models.Item, item_id)
    if item is None or item.list_id != list_id:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    await manager.broadcast(list_id, {"type": "item_removed", "item_id": item_id})
    return None
