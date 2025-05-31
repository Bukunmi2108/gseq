# FastAPI Starter Kit
A professional FastAPI template
<p>
    <a href="https://github.com/MahmudJewel/fastapi-starter-boilerplate/fork">
        <img src="https://img.shields.io/github/forks/MahmudJewel/fastapi-starter-kit.svg?style=social&label=Fork" />
    </a>
    <a href="https://github.com/MahmudJewel/fastapi-starter-boilerplate/fork">
        <img src="https://img.shields.io/github/stars/MahmudJewel/fastapi-starter-kit.svg?style=social&label=Stars" />
    </a>
    <a href="https://github.com/MahmudJewel/fastapi-starter-boilerplate/fork">
        <img src="https://img.shields.io/nuget/dt/Azylee.Core.svg" />
    </a>
</p>
<p>
    If the repo is helpful, please give a star and fork it.
</p>
<a href="https://github.com/MahmudJewel/fastapi-starter-boilerplate/fork">
    Click here to clone/fork the repository
</a>

<!-- [![Fork](https://img.shields.io/github/forks/MahmudJewel/fastapi-starter-kit.svg?style=social&label=Fork)](https://github.com/MahmudJewel/fastapi-starter-kit/fork)
[![Stars](https://img.shields.io/github/stars/MahmudJewel/fastapi-starter-kit.svg?style=social&label=Stars)](https://github.com/MahmudJewel/fastapi-starter-kit)
[![NuGet](https://img.shields.io/nuget/dt/Azylee.Core.svg)](https://www.nuget.org/packages/Azylee.Core)   -->

## Features:

- FastAPI project structure tree
- user module
  - id, first name, last name, **email** as username, **password**, role, is_active created_at, updated_at
- admin dashboard => sqladmin
- authentication => JWT
- db migration => alembic
- CORS middleware

## Structured Tree

```sh
├── alembic     # Manages database migrations
├── alembic.ini
├── app
│   ├── api
│   │   ├── endpoints   # Contains modules for each feature (user, product, payments).
│   │   │   ├── __init__.py
│   │   │   └── user
│   │   │       ├── auth.py
│   │   │       ├── functions.py
│   │   │       ├── __init__.py
│   │   │       └── user.py
│   │   ├── __init__.py
│   │   └── routers     # Contains FastAPI routers, where each router corresponds to a feature.
│   │       ├── main_router.py
│   │       ├── __init__.py
│   │       └── user.py
│   ├── core    # Contains core functionality like database management, dependencies, etc.
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── __init__.py
│   ├── main.py     # Initializes the FastAPI app and brings together various components.
│   ├── models      # Contains modules defining database models for users, products, payments, etc.
│   │   ├── admin.py
│   │   ├── common.py
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas   # Pydantic model for data validation
│   │   ├── __init__.py
│   │   └── user.py
│   └── utils       # Can include utility functions that are used across different features.
├── requirements.txt # Lists project dependencies.
```

**app/api/endpoints/**: Contains modules for each feature (user, product, payments).

**app/api/routers/**: Contains FastAPI routers, where each router corresponds to a feature.

**app/models/**: Contains modules defining database models for users, products, payments, etc.

**app/core/**: Contains core functionality like database management, dependencies, etc.

**app/utils/**: Can include utility functions that are used across different features.

**app/main.py**: Initializes the FastAPI app and brings together various components.

**tests/**: Houses your test cases.

**alembic/**: Manages database migrations.

**docs/**: Holds documentation files.

**scripts/**: Contains utility scripts.

**requirements.txt**: Lists project dependencies.

# Setup

The first thing to do is to clone the repository:

```sh
$ https://github.com/MahmudJewel/fastapi-starter-boilerplate
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ cd fastapi-starter-boilerplate
$ python -m venv venv
$ source venv/bin/activate
```

Then install the dependencies:

```sh
# for fixed version
(venv)$ pip install -r requirements.txt

# or for updated version
(venv)$ pip install -r dev.txt
```

Note the `(venv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies:

```sh
# db migrations
(venv)$ alembic upgrade head

# start the server
(venv)$ fastapi dev app/main.py # using fastapi CLI ==> after version 0.100.0
or
(venv)$ uvicorn app.main:app --reload # using directly uvicorn ==> old one => before version 0.100.0
```

## API Endpoint Summary

**Base URL:** `/api/v1` (Please confirm with `settings.API_V1_STR` if different)

**Authentication:**
*   Most endpoints require a JWT Bearer token provided in the `Authorization` header (e.g., `Authorization: Bearer <your_token>`).
*   **Login:** `POST /user/login`
    *   Request: `{ "email": "user@example.com", "password": "password" }`
    *   Response: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
*   **Refresh Token:** `POST /user/refresh_token?refresh_token={token}`
    *   Response: `{ "access_token": "...", "token_type": "bearer" }`
*   **Get Current User:** `GET /user/me`
    *   Response: `UserSchema` (details of the authenticated user).

---

**I. User Management (General)**

*   **Create Generic User:** `POST /user/`
    *   Request: `UserCreate` schema (likely includes email, password, first_name, last_name, role).
    *   Response: `UserSchema`.
    *   *Frontend Usage:* If a general user registration form is needed, distinct from specific student/teacher roles. Authorization for this endpoint should be reviewed (e.g., Admin-only or self-registration for basic 'USER' role).
*   **List All Users:** `GET /user/`
    *   Response: `List[UserSchema]`.
    *   *Frontend Usage:* Admin panel - user listing and management. (Requires Admin privileges).
*   **Get User by ID:** `GET /user/{user_id}`
    *   Response: `UserSchema`.
    *   *Frontend Usage:* Admin panel - view specific user details; Users viewing their own profile if `user_id` is theirs.
*   **Update User:** `PATCH /user/{user_id}`
    *   Request: `UserUpdate` schema (fields to update).
    *   Response: `UserSchema`.
    *   *Frontend Usage:* User profile editing form. Authorization needs clarity (e.g., self-update or Admin only).
*   **Delete User:** `DELETE /user/{user_id}`
    *   Response: Success/failure message or deleted user object.
    *   *Frontend Usage:* Admin panel - delete user functionality. (Requires Admin privileges).

---

**II. Student Management**

*   **Create Student:** `POST /student/create` (Admin Only)
    *   Request: `StudentCreate` schema (e.g., email, password, first_name, last_name, admin_no).
    *   Response: `StudentSchema`.
    *   *Frontend Usage:* Admin panel - form for adding new student accounts.
*   **List All Students:** `GET /student/all` (Admin/Teacher)
    *   Response: `List[StudentSchema]`.
    *   *Frontend Usage:* Admin/Teacher dashboards for viewing student lists.
*   **Get Student Details:** `GET /student/{student_id}` (Admin/Teacher, or Student for own profile)
    *   Response: `StudentSchema`.
    *   *Frontend Usage:* Viewing detailed student profiles.
*   **Update Student:** `PUT /student/{student_id}` (Admin or Student for own profile)
    *   Request: `StudentCreate` schema (or a specific `StudentUpdate` schema).
    *   Response: `StudentSchema`.
    *   *Frontend Usage:* Editing student information.
*   **Delete Student:** `DELETE /student/{student_id}` (Admin Only)
    *   Response: `StudentSchema` of deleted student.
    *   *Frontend Usage:* Admin panel - removing student accounts.

---

**III. Teacher Management**

*   **Create Teacher:** `POST /teacher/create` (Admin Only)
    *   Request: `TeacherCreate` schema.
    *   Response: `TeacherSchema`.
    *   *Frontend Usage:* Admin panel - form for adding new teacher accounts.
*   **List All Teachers:** `GET /teacher/all` (Admin)
    *   Response: `List[TeacherSchema]`.
    *   *Frontend Usage:* Admin dashboards for viewing teacher lists.
*   **Get Teacher Details:** `GET /teacher/{teacher_id}` (Admin or Teacher for own profile)
    *   Response: `TeacherSchema`.
    *   *Frontend Usage:* Viewing detailed teacher profiles.
*   **Update Teacher:** `PUT /teacher/{teacher_id}` (Admin or Teacher for own profile)
    *   Request: `TeacherCreate` schema (or a `TeacherUpdate` schema).
    *   Response: `TeacherSchema`.
    *   *Frontend Usage:* Editing teacher information.
*   **Delete Teacher:** `DELETE /teacher/{teacher_id}` (Admin Only)
    *   Response: `TeacherSchema` of deleted teacher.
    *   *Frontend Usage:* Admin panel - removing teacher accounts.

---

**IV. Admin User Management** (Primarily for Admins managing other Admins)

*   **Create Admin:** `POST /admin/create_admin` (Admin Only - Note: endpoint path includes `_admin`)
    *   Request: `AdminCreate` schema.
    *   Response: `AdminSchema`.
    *   *Frontend Usage:* Super Admin panel for adding other administrators.
*   Other endpoints like `GET /admin/admins/`, `GET /admin/admins/{admin_id}` etc. are for admin self-management.

---

**V. Subject Management** (CRUD typically Admin-only)

*   **Create Subject:** `POST /subject/create` (Admin Only)
    *   Request: `SubjectCreate` schema (name).
    *   Response: `SubjectSchema`.
    *   *Frontend Usage:* Admin panel - creating new academic subjects.
*   **List All Subjects:** `GET /subject/all`
    *   Response: `List[SubjectSchema]`.
    *   *Frontend Usage:* Displaying subjects for selection in filters (e.g., for practice mode, browsing questions), admin views.
*   **Get Subject by ID:** `GET /subject/{subject_id}`
    *   Response: `SubjectSchema`.
*   **Update Subject:** `PUT /subject/update/{subject_id}` (Admin Only)
*   **Delete Subject:** `DELETE /subject/delete/{subject_id}` (Admin Only)

---

**VI. Question Management**

*   **Create Question:** `POST /question/create` (Admin Only - review if Teachers should also have this right)
    *   Request: `QuestionCreate` schema (type, subject_id, question_text, options (JSON), answer, year, optional image).
    *   Response: `QuestionSchema`.
    *   *Frontend Usage:* Admin/Teacher panel - form for adding new questions, potentially with image upload.
*   **List All Questions:** `GET /question/all`
    *   Response: `List[QuestionSchema]`.
    *   *Frontend Usage:* Admin/Teacher panel - browsing and managing questions.
*   **Get Question by ID:** `GET /question/{question_id}`
*   **Update Question:** `PUT /question/update/{question_id}` (Admin or Teacher)
*   **Delete Question:** `DELETE /question/delete/{question_id}` (Admin Only)
*   **Get Question Image:** `GET /question/{question_id}/image`
    *   Response: Image file (e.g., image/jpeg).
    *   *Frontend Usage:* Displaying images associated with questions.

---

**VII. eLibrary (Book Management)**

*   **Upload/Create Book:** `POST /book/create` (Any Authenticated User - review if restrictions needed)
    *   Request: Multipart form data including `name` (str) and optional `cover_image` (file), `pdf_file` (file).
    *   Response: `BookSchema` (includes `has_cover_image`, `has_pdf`, `likes_count`).
    *   *Frontend Usage:* User section for uploading new books to the library.
*   **List All Books:** `GET /book/all`
    *   Response: `List[BookSchema]`.
    *   *Frontend Usage:* Main eLibrary page for browsing books, with pagination.
*   **Get Book Details:** `GET /book/{book_id}`
    *   Response: `BookSchema`.
    *   *Frontend Usage:* Viewing a specific book's detail page.
*   **Update Book:** `PUT /book/update/{book_id}` (Uploader or Admin - review permissions)
*   **Delete Book:** `DELETE /book/delete/{book_id}` (Uploader or Admin - review permissions)
*   **Like Book:** `POST /book/{book_id}/like`
    *   Response: `BookSchema`.
    *   *Frontend Usage:* "Like" button on a book's detail page.
*   **Increment View Count:** `POST /book/{book_id}/view`
    *   Response: Success message.
    *   *Frontend Usage:* Called automatically when a user accesses a book's content.
*   **Get Book Cover Image:** `GET /book/{book_id}/cover_image`
    *   Response: Image file.
    *   *Frontend Usage:* Displaying book covers.
*   **Get Book PDF:** `GET /book/{book_id}/pdf`
    *   Response: PDF file.
    *   *Frontend Usage:* Opening/embedding PDF for reading.

---

**VIII. Exam Bundle Management (Admin/Teacher Only)**

*   **Create Exam Bundle:** `POST /exam_bundle/create`
    *   Request: `ExamBundleCreate` schema (name, time_in_mins, is_active, subject_combinations `Dict[subject_id_str, num_questions]`, class_ids `List[class_id_str]`).
    *   Response: `ExamBundleSchema`.
    *   *Frontend Usage:* Admin/Teacher panel for creating and configuring formal exams.
*   **List All Exam Bundles:** `GET /exam_bundle/all`
*   **Get Exam Bundle by ID:** `GET /exam_bundle/{exam_bundle_id}`
*   **Update Exam Bundle:** `PUT /exam_bundle/update/{exam_bundle_id}`
*   **Delete Exam Bundle:** `DELETE /exam_bundle/delete/{exam_bundle_id}`

---

**IX. Student Formal Exam Workflow (Student Only)**

*   **List Available Exams:** `GET /student/available_exams`
    *   Response: `List[ExamBundleSchema]` (filtered for the student's class).
    *   *Frontend Usage:* Student dashboard - shows exams they are eligible to take.
*   **Start Exam Attempt:** `POST /student/exam_attempts/{exam_bundle_id}/start`
    *   Response: `{ "attempt": StudentExamAttemptSchema, "questions": List[QuestionSchema] }` (questions do not include answers).
    *   *Frontend Usage:* Student clicks "Start Exam". Frontend receives attempt details and questions to render the exam interface.
*   **Submit Exam Answers:** `POST /student/exam_attempts/{attempt_id}/submit`
    *   Request: `List[StudentAnswerCreateSchema]` (each item: `question_id`, `selected_answer`).
    *   Response: `StudentExamAttemptSchema` (updated with score, status, and list of submitted answers).
    *   *Frontend Usage:* Student submits their completed exam. Frontend can show a summary or confirmation.
*   **List Student's Exam Attempts:** `GET /student/exam_attempts`
    *   Response: `List[StudentExamAttemptSchema]`.
    *   *Frontend Usage:* Student dashboard - history of taken exams.
*   **Get Student's Exam Attempt Result:** `GET /student/exam_attempts/{attempt_id}/result`
    *   Response: `StudentExamAttemptSchema` (includes `answers: List[StudentAnswerSchema]`, where each `StudentAnswerSchema` now contains `selected_answer` and `correct_answer`).
    *   *Frontend Usage:* Student views detailed results of a past exam, including their answers, the correct answers, and score.

---

**X. Student Practice Mode (Student Only)**

*   **Start Practice Session:** `POST /student/practice/sessions/start`
    *   Request: `PracticeSessionCreateSchema` (optional `subject_id`, `question_type`, `year`).
    *   Response: `{ "session": PracticeSessionSchema, "questions": List[QuestionSchema] }` (up to 60 questions, without answers).
    *   *Frontend Usage:* Student selects practice criteria, clicks "Start Practice". Frontend receives session details and questions.
*   **Submit Practice Answers:** `POST /student/practice/sessions/{session_id}/submit`
    *   Request: `List[PracticeSessionAnswerCreateSchema]`.
    *   Response: `PracticeSessionSchema` (updated with score, status, and answers).
    *   *Frontend Usage:* Student submits practice answers. Frontend shows summary/score.
*   **List Student's Practice Sessions:** `GET /student/practice/sessions`
    *   Response: `List[PracticeSessionSchema]`.
    *   *Frontend Usage:* Student dashboard - history of practice sessions.
*   **Get Student's Practice Session Result:** `GET /student/practice/sessions/{session_id}/result`
    *   Response: `PracticeSessionSchema` (includes `answers: List[PracticeSessionAnswerSchema]`, where each answer schema includes `selected_answer` and `correct_answer`).
    *   *Frontend Usage:* Student reviews a past practice session with detailed answers and corrections.

---

## User module's API

| SRL | METHOD   | ROUTE              | FUNCTIONALITY                  | Fields                                                                                |
| --- | -------- | ------------------ | ------------------------------ | ------------------------------------------------------------------------------------- |
| _1_ | _POST_   | `/login`           | _Login user_                   | _**email**, **password**_                                                             |
| _2_ | _POST_   | `/refresh/?refresh_token=`           | _Refresh access token_|_None_ 
| _3_ | _POST_   | `/users/`          | _Create new user_              | _**email**, **password**, first name, last name_                                      |
| _4_ | _GET_    | `/users/`          | _Get all users list_           | _email, password, first_name, last_name, role, is_active, created_at, updated_at, id_ |
| _5_ | _GET_    | `/users/me/`       | _Get current user details_     | _email, password, first_name, last_name, role, is_active, created_at, updated_at, id_ |
| _6_ | _GET_    | `/users/{user_id}` | _Get indivisual users details_ | _email, password, first_name, last_name, role, is_active, created_at, updated_at, id_ |
| _7_ | _PATCH_  | `/users/{user_id}` | _Update the user partially_    | _email, password, is_active, role_                                                    |
| _8_ | _DELETE_ | `/users/{user_id}` | _Delete the user_              | _None_                                                                                |
| _9_ | _GET_    | `/`                | _Home page_                    | _None_                                                                                |
| _10_ | _GET_    | `/admin`           | _Admin Dashboard_              | _None_                                                                                |

# Tools

### Back-end

#### Language:

    Python

#### Frameworks:

    FastAPI
    pydantic

#### Other libraries / tools:

    SQLAlchemy
    starlette
    uvicorn
    python-jose
    alembic

For production level project, Please follow this repo https://github.com/MahmudJewel/fastapi-production-boilerplate
### Happy Coding
