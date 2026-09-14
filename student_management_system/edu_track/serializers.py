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

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"
        validators = []

    def validate(self, attrs):
        course = attrs.get("course")
        year_level = attrs.get("year_level")

        if course is None and self.instance is not None:
            course = self.instance.course
        if year_level is None and self.instance is not None:
            year_level = self.instance.year_level

        if course is not None and year_level is not None:
            if year_level > course.course_duration:
                raise serializers.ValidationError({
                    "year_level": (
                        f"{course} is a {course.get_course_duration_display()} course; "
                        f"Year {year_level} is not available."
                    )
                })

        return attrs

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
        validators = []

    def validate(self, attrs):
        student = attrs.get("student")
        module = attrs.get("module")
        obtained_marks = attrs.get("obtained_marks")

        if module:
            if student and module.semester.course_id != student.enrolled_course_id:
                raise serializers.ValidationError(
                    "The selected module does not belong to the student's enrolled course."
                )

        if module is not None and obtained_marks is not None:
            if obtained_marks < 0:
                raise serializers.ValidationError("Obtained marks cannot be negative.")
            if obtained_marks > module.full_marks:
                raise serializers.ValidationError(
                    f"Obtained marks cannot exceed the module full marks ({module.full_marks})."
                )

        if student and module:
            duplicate_results = Result.objects.filter(student=student, module=module)
            instance = self.instance
            if instance is not None:
                duplicate_results = duplicate_results.exclude(pk=instance.pk)
            if duplicate_results.exists():
                raise serializers.ValidationError(
                    "A result already exists for this student and module."
                )

        return attrs

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"