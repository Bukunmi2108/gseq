from fastapi import APIRouter
from app.api.routers.user import user_router
from app.api.endpoints.book.book import router as book_router
from app.api.endpoints.exam_bundle.exam_bundle import router as exam_bundle_router
from app.api.endpoints.question.question import router as question_router
from app.api.endpoints.subject.subject import router as subject_router
from app.api.endpoints.student.student import router as student_router
from app.api.endpoints.teacher.teacher import router as teacher_router
from app.api.endpoints.student_exam import router as student_exam_router

router = APIRouter()

router.include_router(user_router)
router.include_router(book_router)
router.include_router(exam_bundle_router)
router.include_router(question_router)
router.include_router(subject_router)
router.include_router(student_router)
router.include_router(teacher_router)
router.include_router(student_exam_router)