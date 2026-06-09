from django.urls import path
from . import views


urlpatterns = [
path("course/", views.list_courses, name = "course_list"),
path("course/add/", views.course_add, name = "course_add"),
path("course/update/<int:id>/", views.course_update, name = "course_update"),
path("course/delete/<int:id>", views.course_delete, name = "course_delete"),
]