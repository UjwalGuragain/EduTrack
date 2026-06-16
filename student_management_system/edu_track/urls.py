from django.urls import path
from . import views

urlpatterns = [
path("login/", views.user_login, name = "login"),
path("register/", views.user_register, name = "register"),
path("logout/", views.user_logout, name = "logout"),


path("instructor-dashboard/", views.instructor_dashboard, name = "instructor_dashboard"),
path("student-dashboard/", views.student_dashboard, name = "student_dashboard"),

path("course/", views.list_courses, name = "course_list"),
path("course/add/", views.course_add, name = "course_add"),
path("course/update/<int:id>/", views.course_update, name = "course_update"),
path("course/delete/<int:id>", views.course_delete, name = "course_delete"),

path("student/", views.list_students, name = "student_list"),
path("student/add/", views.student_add, name = "student_add"),
path("student/update/<int:id>/", views.student_update, name = "student_update"),
path("student/delete/<int:id>", views.student_delete, name = "student_delete"),

path("module/", views.list_modules, name = "module_list"),
path("module/add/", views.module_add, name = "module_add"),
path("module/update/<int:id>/", views.module_update, name = "module_update"),
path("module/delete/<int:id>/", views.module_delete, name = "module_delete"),

path("result/", views.list_result, name = "result_list"),
path("result/add/", views.result_add, name = "result_add"),
path("result/update/<int:id>/", views.result_update, name = "result_update"),
path("result/delete/<int:id>/", views.result_delete, name = "result_delete"),

path("attendance/", views.list_attendance, name = "attendance_list"),
path("attendance/add/", views.attendance_add, name = "attendance_add"),
path("attendance/update/<int:id>/", views.attendance_update, name = "attendance_update"),
path("attendance/delete/<int:id>/", views.attendance_delete, name = "attendance_delete")
]