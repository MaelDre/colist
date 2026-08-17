from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)


class ItemOut(BaseModel):
    id: str
    name: str
    last_edited_by_color: str
    last_edited_at: datetime

    model_config = {"from_attributes": True}


class PresenceEntry(BaseModel):
    session_id: str
    color: str


class ListOut(BaseModel):
    id: str
    created_at: datetime
    items: list[ItemOut]
    presence: list[PresenceEntry]

    model_config = {"from_attributes": True}


class ListCreateOut(BaseModel):
    id: str
