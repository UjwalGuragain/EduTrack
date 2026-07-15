from rest_framework import serializers
from .models import *

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class StudentSerializer(serializers.ModelSerializer):
    enrolled_course = CourseSerializer(read_only = True)

    class Meta:
        model = Student
        fields = "__all__"

class StudentHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = [
            "url",
            "full_name",
            "email",
            "contact_number",
            "enrollment_number"
            "enrolled_course"
        ]

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = "__all__"

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"