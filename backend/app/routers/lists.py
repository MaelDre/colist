from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.session import get_or_create_session
from app.state import store

router = APIRouter(prefix="/api/lists", tags=["lists"])


@router.post("", response_model=schemas.ListCreateOut, status_code=201)
def create_list(db: Session = Depends(get_db)):
    new_list = models.List()
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return schemas.ListCreateOut(id=new_list.id)


@router.get("/{list_id}", response_model=schemas.ListOut)
def get_list(list_id: str, request: Request, response: Response, db: Session = Depends(get_db)):
    db_list = db.get(models.List, list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")

    get_or_create_session(list_id, request, response)
    presence = store.get(list_id).presence_snapshot()

    return schemas.ListOut(
        id=db_list.id,
        created_at=db_list.created_at,
        items=[schemas.ItemOut.model_validate(item) for item in db_list.items],
        presence=[schemas.PresenceEntry(**p) for p in presence],
    )


@router.delete("/{list_id}", status_code=204)
def delete_list(list_id: str, db: Session = Depends(get_db)):
    db_list = db.get(models.List, list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    db.delete(db_list)
    db.commit()
    store.drop(list_id)
    return None
