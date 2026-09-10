def user_role(request):
    user = getattr(request, "user", None)
    return {
        "is_instructor": (
            hasattr(user, "instructor")
        ),
        "is_student": (
            hasattr(user, "student")
        ),
    }