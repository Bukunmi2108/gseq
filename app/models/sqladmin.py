from sqladmin import ModelView
from app.models import User, Admin, Student, Teacher, Book, Subject, Question, ExamBundle, Term, Session
from app.utils.constant.globals import UserRole

class UserAdmin(ModelView, model=User):
    name_plural = "All Users"
    column_list = [User.id, User.email, User.first_name, User.last_name, User.role, User.is_left, User.created_at]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    column_filters = [User.role, User.is_left]
    column_details_list = [User.id, User.email, User.first_name, User.last_name, User.role, User.is_left, User.created_at, User.updated_at]

class AdminUserAdmin(ModelView, model=Admin):
    name = "Admin User" # Name for single instance
    name_plural = "Admin Users" # Name for multiple instances
    column_list = [Admin.id, Admin.email, Admin.first_name, Admin.last_name, Admin.is_left, Admin.created_at]
    column_searchable_list = [Admin.email, Admin.first_name, Admin.last_name]
    column_filters = [Admin.is_left]

class StudentAdmin(ModelView, model=Student):
    name = "Student User"
    name_plural = "Student Users"
    column_list = [Student.id, Student.email, Student.first_name, Student.last_name, Student.is_left, Student.created_at]
    column_searchable_list = [Student.email, Student.first_name, Student.last_name]
    column_filters = [Student.is_left]


class TeacherAdmin(ModelView, model=Teacher):
    name = "Teacher User"
    name_plural = "Teacher Users"
    column_list = [Teacher.id, Teacher.email, Teacher.first_name, Teacher.last_name, Teacher.is_left, Teacher.created_at]
    column_searchable_list = [Teacher.email, Teacher.first_name, Teacher.last_name]
    column_filters = [Teacher.is_left]


class BookAdmin(ModelView, model=Book):
    column_list = [Book.id, Book.name, Book.uploaded_by_id, Book.views, Book.created_at]
    column_searchable_list = [Book.name]
    column_filters = [Book.uploaded_by_id]

class SubjectAdmin(ModelView, model=Subject):
    column_list = [Subject.id, Subject.name, Subject.created_at]
    column_searchable_list = [Subject.name]


class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.type, Question.question_text, Question.subject_id, Question.answer, Question.created_at]
    column_searchable_list = [Question.question_text]
    column_filters = [Question.type, Question.subject_id]
    # You might want to display the subject name instead of subject_id.


class ExamBundleAdmin(ModelView, model=ExamBundle):
    column_list = [
        ExamBundle.id,
        ExamBundle.name,
        ExamBundle.time_in_mins,
        ExamBundle.is_active,
        ExamBundle.subject_combinations,
        ExamBundle.no_of_participants,
        ExamBundle.uploaded_by_id,
        ExamBundle.created_at
    ]
    column_searchable_list = [ExamBundle.name]
    column_filters = [ExamBundle.is_active, ExamBundle.uploaded_by_id]
    # For subject_combinations (JSON type), you might need a custom formatter for better display.


class TermAdmin(ModelView, model=Term):
    column_list = [Term.id, Term.name, Term.session_id, Term.created_at]
    column_searchable_list = [Term.name]
    column_filters = [Term.name, Term.session_id] # Filter by AcademicTerm enum


class SessionAdmin(ModelView, model=Session):
    column_list = [Session.id, Session.name, Session.start_date, Session.end_date, Session.created_at]
    column_searchable_list = [Session.name]
    column_filters = [Session.start_date, Session.end_date]