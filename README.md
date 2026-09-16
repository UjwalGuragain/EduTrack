# 🎓 EduTrack

**EduTrack** is a role-based education management system designed to make student, instructor, and academic data easier to manage, access, and secure.

The project focuses on building a structured backend where users can perform actions based on **who they are, what they are requesting, and whether they have permission to perform that action**.

---

## 📌 Overview

EduTrack is being developed with a strong focus on:

* 🔐 Authentication
* 🛡️ Authorization and access control
* 👥 Role-based permissions
* 🎓 Student management
* 👨‍🏫 Instructor management
* 📚 Academic data management
* 📊 Structured data access
* 🔒 Protecting users from accessing data they are not permitted to see

A major goal of EduTrack is to understand the difference between:

> **Authentication:** Who is the user?

and

> **Authorization:** What is this user allowed to do?

For example, knowing that a user is an instructor does not automatically mean that the instructor can access every protected operation. EduTrack is designed to enforce permissions at the appropriate level.

---

## 🏗️ Core Concept

EduTrack follows a simple authorization flow:

```text
                 ┌──────────────┐
                 │    Request   │
                 └──────┬───────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Who is the user?  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ What is requested?│
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Which model/object│
              │ is being accessed?│
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Is the action     │
              │ permitted?        │
              └─────────┬─────────┘
                   ┌────┴────┐
                   │         │
                  YES        NO
                   │         │
                   ▼         ▼
              Allow       Deny
```

This helps prevent authorization from becoming a simple:

```text
if user.role == "instructor":
    allow()
```

Instead, access should consider the **user, action, resource, and scope of the requested data**.

---

## 🔐 Authentication vs Authorization

### Authentication

Authentication answers:

> **"Who are you?"**

Examples:

* Logging in with credentials
* Verifying a user's identity
* Creating a user session/token

### Authorization

Authorization answers:

> **"What are you allowed to access or modify?"**

Examples:

* Can a student view their own profile?
* Can an instructor manage student records?
* Can an administrator view all students?
* Can an instructor modify student grades?
* Can a student modify their own academic records?

EduTrack treats these as separate concerns.

---

## 👥 Roles

The system is designed around different user roles.

| Role          | Example Responsibilities                       |
| ------------- | ---------------------------------------------- |
| 👑 Admin      | Manage and oversee the system                  |
| 👨‍🏫 Instructor | Manage student and academic information |
| 🎓 Student    | Access their own permitted information         |

The current permissions are defined by the application's decorators, API
permission classes, and object-level ownership checks.

---

## 🛡️ Object-Level Access Control

One important part of EduTrack is **object-level authorization**.

For example:

```text
Student A → requests Student A's profile
Student A → requests Student B's profile
```

Even if Student A is authenticated, authentication alone does not mean Student A should be allowed to access Student B's information.

Therefore, EduTrack needs to check both:

```text
Is the user authenticated?
        +
Is the user authorized to access this specific object?
```

---

## 📋 Collection-Level Access Control

Object-level permission is not the only concern.

Consider:

```text
GET /students/
```

A system might correctly prevent:

```text
GET /students/123
```

from returning another student's private information while accidentally allowing a user to retrieve the entire student collection.

Therefore, EduTrack also considers **collection/list-level permissions**.

For example:

```text
Can this user access this specific student?
```

is different from:

```text
Can this user access the list of students?
```

Authorization must therefore consider both **individual resources and collections of resources**.

---

## 🧩 Authorization Model

A useful way to think about EduTrack's permission system is:

```text
User
 │
 ├── Role
 │
 ├── Action
 │
 ├── Resource / Model
 │
 ├── Object
 │
 └── Scope
        │
        ▼
   Authorization
        │
   ┌────┴────┐
   ▼         ▼
 Allow      Deny
```

For every request, the system should be able to answer:

1. **Who is making the request?**
2. **What action are they trying to perform?**
3. **What resource/model are they accessing?**
4. **Which specific object is involved?**
5. **What scope of data are they trying to access?**
6. **Does their role and permission allow this action?**

---

## 🗂️ Example Permissions

A simplified example:

| Action                          | Student | Instructor | Admin/staff |
| ------------------------------- | ------- | ---------- | ----------- |
| View own profile                | ✅      | ✅         | ✅          |
| View another student's profile  | ❌      | ✅         | ✅          |
| View student list               | ❌      | ✅         | ✅          |
| Modify own academic records     | ❌      | ❌         | ✅          |
| Modify student records          | ❌      | ✅         | ✅          |
| Download attendance/result PDFs | ❌      | ✅         | ✅          |

These are the current application permissions.

---

## 🌐 REST APIs

EduTrack exposes its application functionality through **RESTful APIs** using the Django REST Framework (DRF).

The project uses **ModelViewSet** to provide a structured way of implementing CRUD operations while keeping the API logic organized and reusable.

### 🔧 ModelViewSets

EduTrack uses DRF's `ModelViewSet` for resources that require standard CRUD operations.

A typical ViewSet follows this pattern:

```python
from rest_framework.viewsets import ModelViewSet

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [
        IsAdminOrStudentReadOnly,
        IsStudentOwnerOrReadOnly,
    ]
```

This allows the API to support common operations such as:

| HTTP Method | Operation           | Example                      |
| ----------- | ------------------- | ---------------------------- |
| `GET`       | List resources      | `GET /api/v1/students/`         |
| `GET`       | Retrieve a resource | `GET /api/v1/students/{id}/`    |
| `POST`      | Create a resource   | `POST /api/v1/students/`        |
| `PUT`       | Update a resource   | `PUT /api/v1/students/{id}/`    |
| `PATCH`     | Partially update    | `PATCH /api/v1/students/{id}/`  |
| `DELETE`    | Delete a resource   | `DELETE /api/v1/students/{id}/` |

### 🔗 API Routing

ViewSets are registered with routers, allowing URL patterns to be generated automatically.

For example:

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("students", StudentViewSet)

urlpatterns = router.urls
```

This produces endpoints such as:

```text
/api/v1/students/
/api/v1/students/{id}/
```

The use of routers reduces repetitive URL configuration and keeps API routing consistent across resources.

---

## 🔐 API Authentication & Authorization

Authentication and authorization are handled separately within the API.

A request generally follows this flow:

```text
Client
  │
  ▼
API Request
  │
  ▼
Authentication
  │
  ├── Not authenticated ──► 401 Unauthorized
  │
  ▼
Authenticated User
  │
  ▼
Permission Check
  │
  ├── Not permitted ──────► 403 Forbidden
  │
  ▼
ViewSet
  │
  ▼
Serializer
  │
  ▼
Model / Database
  │
  ▼
API Response
```

This separation allows EduTrack to determine both:

* **Who the user is**
* **Whether that user is allowed to perform the requested action**

---

## 🛡️ Permissions in ViewSets

Permissions can be applied directly to ViewSets.

For example:

```python
class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [
        IsAdminOrStudentReadOnly,
        IsStudentOwnerOrReadOnly,
    ]
```

For more complex requirements, EduTrack can use custom permission classes.

For example:

```text
Student
   │
   ├── Can view own information
   └── Cannot access another student's information

Instructor
   │
   ├── Can manage student records
   └── Cannot manage instructor records

Admin
   │
   └── Can access permitted system-wide resources
```

This is particularly important because simply protecting an endpoint with `IsAuthenticated` does **not** automatically mean every authenticated user should have access to every object.

---

## 🎯 Object-Level Authorization

ModelViewSets provide endpoints for individual objects, making object-level authorization especially important.

For example:

```text
GET /api/v1/students/15/
```

The API should not only ask:

```text
Is the requester authenticated?
```

It should also ask:

```text
Is this requester allowed to access Student #15?
```

This allows EduTrack to protect individual student records rather than relying only on broad role-based checks.

---

## 📋 Collection-Level Authorization

Authorization is also required for list endpoints.

For example:

```text
GET /api/v1/students/
```

is different from:

```text
GET /api/v1/students/15/
```

The first request asks for a **collection of students**, while the second requests a **specific student**.

Therefore, EduTrack considers both:

```text
Collection-level permissions
        +
Object-level permissions
```

This helps prevent situations where a user cannot access another student's individual endpoint but can still retrieve the same student's information through a list endpoint.

---

## 🔄 API CRUD Operations

The ModelViewSet approach provides a consistent CRUD interface across EduTrack resources.

```text
                    REST API
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Students     Instructors  Other Models
          │            │            │
          ▼            ▼            ▼
       ViewSet       ViewSet       ViewSet
          │            │            │
          └────────────┼────────────┘
                       ▼
                  Permissions
                       │
                       ▼
                   Serializer
                       │
                       ▼
                    Model
                       │
                       ▼
                   Database
```

This architecture keeps API endpoints predictable while allowing each resource to have its own authentication, authorization, validation, and business rules.

---

## 🧪 API Testing

REST API endpoints should be tested for both **functionality and security**.

Examples include:

```text
GET /api/v1/students/
    ├── Authenticated user       → expected response
    └── Unauthenticated user     → denied

GET /api/v1/students/15/
    ├── Authorized user          → expected response
    └── Unauthorized user        → denied

POST /api/v1/students/
    ├── User with create access  → allowed
    └── User without create access → denied

PATCH /api/v1/students/15/
    ├── Authorized user          → allowed
    └── Unauthorized user        → denied
```

The goal is to verify that every API endpoint enforces the intended access-control rules.

---

## 🧱 API Design Principles

EduTrack's REST API follows these principles:

* **Resource-oriented endpoints**
* **HTTP methods for CRUD operations**
* **ModelViewSets for reusable API logic**
* **Routers for consistent URL configuration**
* **Serializers for validation and representation**
* **Authentication before authorization**
* **Object-level access control**
* **Collection-level access control**
* **Automated permission testing**
* **Least-privilege access**

This provides a foundation for expanding EduTrack with additional resources without duplicating API logic.

## 🏛️ Project Architecture

The project is being developed with separation of responsibilities in mind.

```text
EDUTRACK/
├── student_management_system/
│   ├── edu_track/
│   │   ├── migrations/
│   │   ├── static/
│   │   ├── templates/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── analytics.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── decorators.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── media/
│   ├── student_management_system/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── settings_production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── db.sqlite3
│   └── manage.py
├── .env
├── .gitignore
└── README.md
```

The exact structure may change as development continues.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip
- virtual environment support

### Setup

```bash
# clone the project
git clone https://github.com/UjwalGuragain/EduTrack.git
cd EduTrack

# create a virtual environment
python -m venv myenv

# activate it
# Windows
myenv\Scripts\activate
# macOS/Linux
source myenv/bin/activate

# install dependencies
pip install -r requirements.txt
```

### Database + app startup

```bash
cd student_management_system
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open:

- http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

### Environment variables

Create a `.env` file in the project root if you plan to use email-based password reset features:

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## 🔌 API Overview

The project exposes a DRF router under `/api/v1/`.

Available endpoints:

- `/api/v1/students/`
- `/api/v1/instructors/`
- `/api/v1/courses/`
- `/api/v1/academic-years/`
- `/api/v1/semesters/`
- `/api/v1/modules/`
- `/api/v1/attendances/`
- `/api/v1/results/`
- `/api/v1/analytics/instructor/`
- `/api/v1/analytics/student/`

Authorization expectations:

- Unauthenticated users are denied access
- Students can read only their own student, attendance, and result records
- Instructors can CRUD students, courses, modules, attendance, and results
- Instructors can view instructors and edit only their own instructor profile
- Admin/staff users can CRUD all protected resources, including instructors
- Attendance and result PDF exports are restricted to instructors and admin/staff
- Result marks are validated against the module full marks (no negative or over-limit values)
- A student can have at most one result per module (duplicate rows are rejected)
- A result must use a module from the student's enrolled course
- Instructor analytics are available to instructors and admin/staff users
- Student analytics are restricted to the authenticated student's own records
- Analytics endpoints are read-only and return chart-ready aggregate data

---

## 🧪 Testing

Testing is an important part of EduTrack, especially for authorization.

Tests should verify not only that permitted users can perform actions, but also that unauthorized users **cannot**.

Examples:

```text
Student can access their own data        → PASS
Student accesses another student's data → DENY
Instructor manages student records      → PASS
Admin accesses permitted resources      → PASS
Unauthorized collection access          → DENY
```

Authorization tests are especially important because a system can appear to work correctly while still exposing data through an overlooked endpoint or query.

The current Django suite contains 60 tests covering role-based access,
object-level permissions, report restrictions, grading behavior, result
validation rules, error pages, safe web CRUD workflows, and advanced
analytics access and calculations.

---

## 📈 Advanced Analytics

EduTrack includes role-specific analytics dashboards powered by the Chart.js
library bundled with AdminLTE.

### Instructor analytics

Available at `/instructor/analytics/` for instructors and admin/staff users:

* Grade distribution
* Attendance trend for the last 30 days
* Student enrollment by course
* Enrollment totals by month
* Average score by course
* Average score by module
* Top-performing students
* Students needing academic attention

### Student analytics

Available at `/student/analytics/` for authenticated students:

* Module scores compared with full marks
* Personal grade distribution
* Personal attendance trend for the last 30 days
* Grade history by module
* Summary statistics for the student's own results

Analytics are calculated server-side in `edu_track/analytics.py`. Student
analytics are scoped to the authenticated student's records, while instructor
analytics use the available academic data for the institution.

---

## 🔒 Security Principles

EduTrack aims to follow these principles:

* **Least privilege** — users should receive only the access they need.
* **Deny by default** — access should not be granted unless explicitly permitted.
* **Defense in depth** — authorization should not depend on a single check.
* **Object-level authorization** — permissions should apply to individual resources where necessary.
* **Collection-level authorization** — list endpoints must also be protected.
* **Separation of concerns** — authentication and authorization should remain distinct.
* **Test permissions** — access-control rules should be covered by automated tests.
* **Safe mutations** — web deletion actions use CSRF-protected POST requests.

---

## 🚧 Project Status

**EduTrack is currently under active development.**

The core management, authorization, reporting, grading, semester
tracking, and analytics workflows are implemented.

### Current Focus

* [x] Understand authentication
* [x] Understand authorization
* [x] Understand role-based access control
* [x] Understand object-level permissions
* [x] Understand collection-level permissions
* [x] Implement permission architecture
* [x] Add comprehensive authorization tests
* [x] Expand student management
* [x] Expand instructor management
* [x] Add academic grading and report features
* [x] Improve documentation
* [x] Add semester tracking
* [x] Add advanced analytics

---

## 🎯 Goals

The long-term goal of EduTrack is to provide a secure and maintainable education management platform while keeping authorization rules clear and understandable.

The project prioritizes:

```text
Security
   ↓
Correct Authorization
   ↓
Clean Architecture
   ↓
Reliable Data Access
   ↓
Useful Education Features
```

---

## 🤝 Contributing

Contributions are welcome.

### How to contribute

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-improvement
   ```
3. Make your changes and keep them focused.
4. Add or update tests for any behavior change.
5. Run the project test suite and confirm it passes.
6. Open a pull request with a clear description of the change.

### Coding guidelines

- Follow the current Django project structure and app conventions.
- Keep authorization checks explicit and test-covered.
- Prefer small, reviewable commits.
- Update the documentation when behavior changes.

---

## 📄 License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026 Ujwal Guragain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⭐ EduTrack

> **Learn. Manage. Protect. Track.**

EduTrack aims to make educational data management structured, secure, and accessible to the right people — while ensuring that the wrong people cannot access it.
