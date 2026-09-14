from django.contrib import admin
from .forms import SemesterForm
from .models import (
    AcademicYear,
    Attendance,
    Course,
    Instructor,
    Module,
    Result,
    Semester,
    Student,
)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("year_label", "start_date", "end_date")
    search_fields = ("year_label",)
    ordering = ("-start_date",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    form = SemesterForm
    list_display = (
        "name",
        "course",
        "academic_year",
        "year_level",
        "semester_number",
        "start_date",
        "end_date",
    )
    list_filter = ("academic_year", "course", "year_level", "semester_number")
    search_fields = ("name", "course__course_name", "course__course_code")
    list_select_related = ("course", "academic_year")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("module_code", "module_name", "semester", "full_marks")
    list_filter = ("semester__academic_year", "semester__course", "semester__year_level")
    search_fields = ("module_code", "module_name")
    list_select_related = ("semester", "semester__course", "semester__academic_year")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "module", "get_semester", "obtained_marks")
    list_filter = ("module__semester__academic_year", "module__semester__course")
    search_fields = (
        "student__full_name",
        "student__enrollment_number",
        "module__module_code",
        "module__module_name",
    )
    list_select_related = ("student", "module", "module__semester")

    @admin.display(description="Semester")
    def get_semester(self, result):
        return result.module.semester


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_code", "course_name", "course_duration")
    search_fields = ("course_code", "course_name")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("enrollment_number", "full_name", "enrolled_course", "email")
    list_filter = ("enrolled_course",)
    search_fields = ("enrollment_number", "full_name", "email")
    list_select_related = ("enrolled_course",)


admin.site.register(Attendance)
admin.site.register(Instructor)