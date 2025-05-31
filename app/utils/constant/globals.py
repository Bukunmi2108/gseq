from enum import Enum as PythonEnum

class UserRole(str, PythonEnum):
    USER = "user"
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class QuestionType(str, PythonEnum):
    SCHOOL = "school"
    JAMB = "jamb"
    WAEC = "waec"
    NECO = "neco"

class AcademicTerm(str, PythonEnum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"