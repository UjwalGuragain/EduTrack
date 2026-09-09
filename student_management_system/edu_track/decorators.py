from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

def instructor_required(view_func):
    """
    This function mandates the requirement of the user --> INSTRUCTOR
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if hasattr(request.user, "instructor"):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def admin_or_staff_required(view_func):
    """
    This function mandates the requirement of the user --> ADMIN/STAFF
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_staff:
            return view_func(request, *args, **kwargs)

        if hasattr(request.user, "instructor"):
            from django.contrib import messages
            messages.error(request, "Only admins can manage instructors.")
            return redirect("instructor_dashboard")

        if hasattr(request.user, "student"):
            from django.contrib import messages
            messages.error(request, "Only admins can manage instructors.")
            return redirect("student_dashboard")

        return redirect("login")
    return wrapper


def admin_or_instructor_required(view_func):
    """
    This function mandates the requirement of the user --> ADMIN/STAFF OR INSTRUCTOR.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_staff or hasattr(request.user, "instructor"):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def student_required(view_func):
    """
    This function mandates the requirement of the user --> STUDENT
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "student"):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper