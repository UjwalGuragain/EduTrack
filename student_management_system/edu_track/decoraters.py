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

        if not hasattr(request.user, "instructor"):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
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