def user_role(request):
    return {
        "is_instructor": (
            hasattr(request.user, "instructor")
        ),
        "is_student": (
            hasattr(request.user, "student")
        ),
    }