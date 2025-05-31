from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class BookBase(BaseModel):
    name: str

class BookCreate(BookBase):
    pass

class BookSchema(BookBase):
    id: UUID
    uploaded_by_id: UUID
    views: int
    likes_count: int = 0
    has_cover_image: bool = False
    has_pdf: bool = False

    model_config = {'from_attributes': True}
