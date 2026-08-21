# 🎓 EduTrack

**EduTrack** is a role-based education management system designed to make student, teacher, and academic data easier to manage, access, and secure.

The project focuses on building a structured backend where users can perform actions based on **who they are, what they are requesting, and whether they have permission to perform that action**.

---

## 📌 Overview

EduTrack is being developed with a strong focus on:

* 🔐 Authentication
* 🛡️ Authorization and access control
* 👥 Role-based permissions
* 🎓 Student management
* 👨‍🏫 Teacher management
* 📚 Academic data management
* 📊 Structured data access
* 🔒 Protecting users from accessing data they are not permitted to see

A major goal of EduTrack is to understand the difference between:

> **Authentication:** Who is the user?

and

> **Authorization:** What is this user allowed to do?

For example, knowing that a user is a teacher does not automatically mean that the teacher can access every student or every piece of student information. EduTrack is designed to enforce permissions at the appropriate level.

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
if user.role == "teacher":
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
* Can a teacher view students assigned to them?
* Can an administrator view all students?
* Can a teacher modify student grades?
* Can a student modify their own academic records?

EduTrack treats these as separate concerns.

---

## 👥 Roles

The system is designed around different user roles.

| Role          | Example Responsibilities                       |
| ------------- | ---------------------------------------------- |
| 👑 Admin      | Manage and oversee the system                  |
| 👨‍🏫 Teacher | Manage or access assigned academic information |
| 🎓 Student    | Access their own permitted information         |

The exact permissions for each role can evolve as the system develops.

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

| Action                         | Student     | Teacher               | Admin                 |
| ------------------------------ | ----------- | --------------------- | --------------------- |
| View own profile               | ✅           | ✅                     | ✅                     |
| View another student's profile | ❌           | Depends on scope      | ✅                     |
| View student list              | ❌ / Limited | Assigned students     | ✅                     |
| Modify own academic records    | ❌           | ❌                     | Depends on permission |
| Modify student records         | ❌           | Depends on permission | ✅                     |

These permissions are examples and may change as EduTrack evolves.

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
    permission_classes = [IsAuthenticated]
```

This allows the API to support common operations such as:

| HTTP Method | Operation           | Example                      |
| ----------- | ------------------- | ---------------------------- |
| `GET`       | List resources      | `GET /api/students/`         |
| `GET`       | Retrieve a resource | `GET /api/students/{id}/`    |
| `POST`      | Create a resource   | `POST /api/students/`        |
| `PUT`       | Update a resource   | `PUT /api/students/{id}/`    |
| `PATCH`     | Partially update    | `PATCH /api/students/{id}/`  |
| `DELETE`    | Delete a resource   | `DELETE /api/students/{id}/` |

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
/api/students/
/api/students/{id}/
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
    permission_classes = [IsAuthenticated]
```

For more complex requirements, EduTrack can use custom permission classes.

For example:

```text
Student
   │
   ├── Can view own information
   └── Cannot access another student's information

Teacher
   │
   ├── Can access assigned students
   └── Cannot access unrelated student records

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
GET /api/students/15/
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
GET /api/students/
```

is different from:

```text
GET /api/students/15/
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
       Students     Teachers     Other Models
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
GET /api/students/
    ├── Authenticated user       → expected response
    └── Unauthenticated user     → denied

GET /api/students/15/
    ├── Authorized user          → expected response
    └── Unauthorized user        → denied

POST /api/students/
    ├── User with create access  → allowed
    └── User without create access → denied

PATCH /api/students/15/
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
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── decorators.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── media/
│   ├── student_management_system/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
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

## 🧪 Testing

Testing is an important part of EduTrack, especially for authorization.

Tests should verify not only that permitted users can perform actions, but also that unauthorized users **cannot**.

Examples:

```text
Student can access their own data        → PASS
Student accesses another student's data → DENY
Teacher accesses assigned students      → PASS
Teacher accesses unauthorized students  → DENY
Admin accesses permitted resources      → PASS
Unauthorized collection access          → DENY
```

Authorization tests are especially important because a system can appear to work correctly while still exposing data through an overlooked endpoint or query.

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

---

## 🚧 Project Status

**EduTrack is currently under active development.**

The project is being developed incrementally, with the current focus on understanding and implementing a solid authentication and authorization architecture before expanding into additional features.

### Current Focus

* [x] Understand authentication
* [x] Understand authorization
* [x] Understand role-based access control
* [x] Understand object-level permissions
* [x] Understand collection-level permissions
* [ ] Implement permission architecture
* [ ] Add comprehensive authorization tests
* [ ] Expand student management
* [ ] Expand teacher management
* [ ] Add academic features
* [ ] Improve documentation

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

EduTrack is currently a learning and development project.

As the project grows, contribution guidelines will be added here.

---

## 📄 License

License information will be added as the project develops.

---

## ⭐ EduTrack

> **Learn. Manage. Protect. Track.**

EduTrack aims to make educational data management structured, secure, and accessible to the right people — while ensuring that the wrong people cannot access it.
