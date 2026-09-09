from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin (staff/superuser) users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsInstructorUser(permissions.BasePermission):
    """Allow access only to users with an Instructor profile."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "instructor")
        )


class IsStudentUser(permissions.BasePermission):
    """Allow access only to users with a Student profile."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "student")
        )


class IsStudentOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission:
    - Students can only access their own Student record (read/write).
    - Instructors and admins can access any Student record.
    - Unauthenticated users denied.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.pk == request.user.student.pk


class IsAttendanceStudentOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission for Attendance:
    - Students can only read (GET/HEAD/OPTIONS) their own attendance records.
    - Instructors and admins can read/write any attendance record.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return obj.student.pk == request.user.student.pk
        return True


class IsResultStudentOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission for Result:
    - Students can only read (GET/HEAD/OPTIONS) their own result records.
    - Instructors and admins can read/write any result record.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return obj.student.pk == request.user.student.pk
        return True


class IsAdminOrInstructorReadOnly(permissions.BasePermission):
    """
    Collection-level permission:
    - Instructors can only list (read) other instructors.
    - Admins can perform any operation on instructors.
    - Unauthenticated users denied.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if hasattr(request.user, "instructor"):
            return request.method in permissions.SAFE_METHODS
        return False


class IsAdminOrInstructorWrite(permissions.BasePermission):
    """
    Collection-level permission for Courses/Modules:
    - Instructors: full CRUD access.
    - Students: read-only access.
    - Unauthenticated: denied.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if hasattr(request.user, "instructor"):
            return True
        if hasattr(request.user, "student"):
            return request.method in permissions.SAFE_METHODS
        return False


class IsAdminOrStudentReadOnly(permissions.BasePermission):
    """
    Collection-level permission for Student list/create/update/delete:
    - Admins: full access.
    - Students: read-only.
    - Instructors: full access (need to see enrolled students).
    - Unauthenticated: denied.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if hasattr(request.user, "instructor"):
            return True
        if hasattr(request.user, "student"):
            return request.method in permissions.SAFE_METHODS
        return False
