from sqlalchemy import Table, Column, ForeignKey
from app.core.base import Base

book_user_likes_association = Table(
    "book_user_likes",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)