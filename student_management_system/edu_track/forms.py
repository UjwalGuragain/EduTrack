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