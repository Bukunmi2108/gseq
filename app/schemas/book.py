from pydantic import BaseModel

class BookBase(BaseModel):
    name: str


class BookCreate(BookBase):
    pass


class BookSchema(BookBase):
    id: int
    uploaded_by_id: int
    views: int

    model_config = {'from_attributes': True}
