from django import forms
from .models import Course, Student, Module, Result, Attendance, Instructor, Semester

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = "__all__"

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = "__all__"

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

class CourseDurationSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        if value:
            try:
                option["attrs"]["data-duration"] = value.instance.course_duration
            except (AttributeError, Course.DoesNotExist):
                pass
        return option


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = "__all__"
        widgets = {
            "course": CourseDurationSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        course_id = self.data.get("course") or self.initial.get("course")
        if not course_id and self.instance.pk:
            course_id = self.instance.course_id

        course = Course.objects.filter(pk=course_id).first()
        max_year = course.course_duration if course else 5
        self.fields["year_level"].choices = [
            choice for choice in Semester.YEAR_LEVEL_CHOICES
            if choice[0] <= max_year
        ]

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        year_level = cleaned_data.get("year_level")
        if course and year_level and year_level > course.course_duration:
            raise forms.ValidationError(
                "The selected year level is not available for this course."
            )
        return cleaned_data

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        module = cleaned_data.get("module")
        obtained_marks = cleaned_data.get("obtained_marks")

        if module:
            if student and module.semester.course_id != student.enrolled_course_id:
                raise forms.ValidationError(
                    "The selected module does not belong to the student's enrolled course."
                )

        if module and obtained_marks is not None:
            full_marks = module.full_marks
            if obtained_marks < 0:
                raise forms.ValidationError("Obtained marks cannot be negative.")
            if obtained_marks > full_marks:
                raise forms.ValidationError(
                    f"Obtained marks cannot exceed the module full marks ({full_marks})."
                )

        if student and module:
            duplicate_results = Result.objects.filter(student=student, module=module)
            if self.instance.pk:
                duplicate_results = duplicate_results.exclude(pk=self.instance.pk)
            if duplicate_results.exists():
                raise forms.ValidationError(
                    "A result already exists for this student and module."
                )

        return cleaned_data

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = "__all__"

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = "__all__"

class InstructorProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ["profile_picture"]

class StudentProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["profile_picture"]