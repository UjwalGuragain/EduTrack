from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

path("", views.user_login, name = "login"),
path("login/", views.user_login, name = "login"),
path("register/", views.user_register, name = "register"),
path("logout/", views.user_logout, name = "logout"),
path("password-reset/", auth_views.PasswordResetView.as_view(
    template_name="edu_track/registration/password_reset.html",
    html_email_template_name="edu_track/registration/password_reset_email.html"), name = "password_reset"),
path("password-reset/done/",auth_views.PasswordResetDoneView.as_view(template_name="edu_track/registration/password_reset_done.html"), name="password_reset_done"),
path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="edu_track/registration/password_reset_confirm.html"), name="password_reset_confirm"),
path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="edu_track/registration/password_reset_complete.html"),name="password_reset_complete"),
path("password-change/", auth_views.PasswordChangeView.as_view(template_name="edu_track/registration/password_change.html"), name = "password_change"),
path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="edu_track/registration/password_change_done.html"), name = "password_change_done"),

path("instructor/dashboard/", views.instructor_dashboard, name = "instructor_dashboard"),
path("student/dashboard/", views.student_dashboard, name = "student_dashboard"),
path("instructor/my-profile/", views.instructor_profile, name = "instructor_profile"),
path("student/my-profile/picture/", views.student_upload_picture, name="student_upload_picture"),
path("instructor/my-profile/picture/", views.instructor_upload_picture, name="instructor_upload_picture"),

path("course/", views.list_courses, name = "course_list"),
path("course/add/", views.course_add, name = "course_add"),
path("course/update/<int:id>/", views.course_update, name = "course_update"),
path("course/delete/<int:id>/", views.course_delete, name = "course_delete"),
path("student/my-course/", views.student_course, name = "student_course"),

path("student/", views.list_students, name = "student_list"),
path("student/add/", views.student_add, name = "student_add"),
path("student/update/<int:id>/", views.student_update, name = "student_update"),
path("student/delete/<int:id>/", views.student_delete, name = "student_delete"),
path("student/my-profile/", views.student_profile, name = "student_profile"),
path("student/student-detail/<int:id>/", views.student_detail, name = "student_detail"),
path("student/export/csv/", views.student_export_csv, name = "student_export_csv"),
path("student/import/csv/", views.student_import_csv, name = "student_import_csv"),

path("module/", views.list_modules, name = "module_list"),
path("module/add/", views.module_add, name = "module_add"),
path("module/update/<int:id>/", views.module_update, name = "module_update"),
path("module/delete/<int:id>/", views.module_delete, name = "module_delete"),
path("student/my-module/", views.student_module, name = "student_module"),

path("result/", views.list_result, name = "result_list"),
path("result/add/", views.result_add, name = "result_add"),
path("result/update/<int:id>/", views.result_update, name = "result_update"),
path("result/delete/<int:id>/", views.result_delete, name = "result_delete"),
path("student/my-result/", views.student_result, name = "student_result"),

path("attendance/", views.list_attendance, name = "attendance_list"),
path("attendance/add/", views.attendance_add, name = "attendance_add"),
path("attendance/update/<int:id>/", views.attendance_update, name = "attendance_update"),
path("attendance/delete/<int:id>/", views.attendance_delete, name = "attendance_delete"),
path("student/my-attendance/", views.student_attendance, name = "student_attendance"),
]