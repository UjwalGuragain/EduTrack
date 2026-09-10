from django import forms
from .models import Course, Student, Module, Result, Attendance, Instructor

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

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        module = cleaned_data.get("module")
        obtained_marks = cleaned_data.get("obtained_marks")

        if student and module and module.courses_id != student.enrolled_course_id:
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