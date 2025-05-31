# fastapi
from fastapi import FastAPI, Depends
from app.core.modules import init_routers, make_middleware
from app.core.database import create_db_tables, create_initial_admin
from app.core.base import engine
import app.models 
from sqladmin import Admin
from app.models.sqladmin import UserAdmin, TeacherAdmin, AdminUserAdmin, StudentAdmin, BookAdmin, SubjectAdmin, QuestionAdmin, ExamBundleAdmin, TermAdmin, SessionAdmin


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Glory Schools Exam App",
        description="This is the Exam and E-learning app for Glory Schools.",
        version="1.0.0",
        # dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    create_db_tables()
    create_initial_admin()

    init_routers(app_=app_)
    return app_


app = create_app()

admin = Admin(app, engine)

admin.add_view(UserAdmin)
admin.add_view(AdminUserAdmin)
admin.add_view(TeacherAdmin)
admin.add_view(BookAdmin)
admin.add_view(SubjectAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(SessionAdmin)
admin.add_view(ExamBundleAdmin)
admin.add_view(TermAdmin)