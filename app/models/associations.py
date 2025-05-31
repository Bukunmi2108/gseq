from sqlalchemy import Table, Column, ForeignKey
from app.core.base import Base

book_user_likes_association = Table(
    "book_user_likes",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

exam_bundle_student_classes_association = Table(
    "exam_bundle_student_classes",
    Base.metadata,
    Column("exam_bundle_id", ForeignKey("exam_bundles.id", ondelete="CASCADE"), primary_key=True),
    Column("student_class_id", ForeignKey("student_classes.id", ondelete="CASCADE"), primary_key=True),
)