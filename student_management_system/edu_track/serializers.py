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
    enrolled_course = CourseSerializer(read_only = False)

    class Meta:
        model = Student
        fields = "__all__"

    def create(self, validated_data):
        course_data = validated_data.pop("enrolled_course")

        course, _ = Course.objects.get_or_create(
            course_name = course_data["course_name"],
            course_duration = course_data["course_duration"],
            course_code = course_data["course_code"]
        )

        student = Student.objects.create(**validated_data, enrolled_course = course)

        return student

    def update(self, instance, validated_data):
        course_data = validated_data.pop("enrolled_course", None)
        if course_data:
            course, _ = Course.objects.get_or_create(
                course_name = course_data.get("course_name", instance.enrolled_course.course_name),
                course_duration = course_data.get("course_duration", instance.enrolled_course.course_duration),
                course_code = course_data.get("course_code", instance.enrolled_course.course_code)
            )
            instance.enrolled_course = course

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class StudentHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = [
            "url",
            "full_name",
            "email",
            "contact_number",
            "enrollment_number",
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