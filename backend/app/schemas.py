from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ItemOut(BaseModel):
    id: str
    name: str
    description: str
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
