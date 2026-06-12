from django.urls import path
from . import views

urlpatterns = [
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

]