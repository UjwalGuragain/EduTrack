from django.contrib import admin
from .models import Course, Module, Student, Result, Attendance

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Student)
admin.site.register(Result)
admin.site.register(Attendance)