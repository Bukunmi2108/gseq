from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException, Response
from app.core.dependencies import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookSchema
from app.api.endpoints.user.functions import get_current_active_user
from sqlalchemy.orm import Session 
from io import BytesIO 
from PIL import Image
from typing import List
from uuid import UUID

router = APIRouter(prefix="/book", tags=['Books'])

@router.post("/create", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cover_image: UploadFile = File(None),  # Optional file upload
    pdf_file: UploadFile = File(None),  # Optional file upload
):
    db_book = Book(
        name=book.name, uploaded_by_id=current_user.id
    ) 

    if cover_image:
        # Basic image validation (content type and size)
        if not cover_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Invalid cover image file type"
            )
        #  resize image
        image_content = await cover_image.read()  # Read the file content
        img = Image.open(BytesIO(image_content))
        img.thumbnail((300, 300))  # Resize to a reasonable size
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')  # Save the resized image
        db_book.cover_image = img_byte_arr.getvalue()

    if pdf_file:
        if pdf_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid PDF file type")
        pdf_content = await pdf_file.read()
        db_book.pdf = pdf_content

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/all", response_model=List[BookSchema])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookSchema)
def read_book(book_id: UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book



@router.put("/update/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: UUID,
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cover_image: UploadFile = File(None),  # Optional file upload
    pdf_file: UploadFile = File(None),  # Optional file upload
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if db_book.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this book"
        )

    db_book.name = book.name

    if cover_image:
        # Basic image validation (content type and size)
        if not cover_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Invalid cover image file type"
            )
        image_content = await cover_image.read()
        img = Image.open(BytesIO(image_content))
        img.thumbnail((300, 300))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        db_book.cover_image = img_byte_arr.getvalue()

    if pdf_file:
        if pdf_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid PDF file type")
        pdf_content = await pdf_file.read()
        db_book.pdf = pdf_content

    db.commit()
    db.refresh(db_book)
    return db_book



@router.delete("/delete/{book_id}", response_model=BookSchema)
async def delete_book(
    book_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if db_book.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this book"
        )

    db.delete(db_book)
    db.commit()
    return db_book


@router.post("/{book_id}/like", response_model=BookSchema)
async def like_book(
    book_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user in db_book.likes:
        raise HTTPException(
            status_code=400, detail="User already liked this book"
        )  # prevent duplicate likes

    db_book.likes.append(current_user)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.post("/{book_id}/view")
def view_book(book_id: UUID, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.views += 1
    db.commit()
    return {"message": "View count updated"}


@router.get("/{book_id}/cover_image")
def get_cover_image(book_id: UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if not book.cover_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover image not found for this book")

    return Response(content=book.cover_image, media_type="image/jpeg")


@router.get("/{book_id}/pdf")
def get_pdf(book_id: UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if not book.pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found for this book")

    return Response(content=book.pdf, media_type="application/pdf")
