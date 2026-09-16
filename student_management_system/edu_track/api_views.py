from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import analytics as analytics_helpers
from .permissions import (
    IsAdminOrInstructorReadOnly,
    IsAdminOrInstructorWrite,
    IsAdminOrStudentReadOnly,
    IsAttendanceStudentOwnerOrReadOnly,
    IsResultStudentOwnerOrReadOnly,
    IsStudentOwnerOrReadOnly,
    IsStudentUser,
)

#API VIEWS
class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrStudentReadOnly, IsStudentOwnerOrReadOnly]

    def get_queryset(self):
        # Students can only see their own record; staff/instructors see all.
        user = self.request.user
        if hasattr(user, "student") and not user.is_staff and not hasattr(user, "instructor"):
            return Student.objects.filter(pk=user.student.pk)
        return super().get_queryset()

class InstructorViewSet(ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorReadOnly]

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite]

class AcademicYearViewSet(ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite]

class SemesterViewSet(ModelViewSet):
    queryset = Semester.objects.select_related("course", "academic_year").all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite]

class ModuleViewSet(ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite]

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite, IsAttendanceStudentOwnerOrReadOnly]

    def get_queryset(self):
        # Students can only see their own attendance.
        user = self.request.user
        if hasattr(user, "student") and not user.is_staff and not hasattr(user, "instructor"):
            return Attendance.objects.filter(student=user.student)
        return super().get_queryset()

class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInstructorWrite, IsResultStudentOwnerOrReadOnly]

    def get_queryset(self):
        # Students can only see their own results.
        user = self.request.user
        if hasattr(user, "student") and not user.is_staff and not hasattr(user, "instructor"):
            return Result.objects.filter(student=user.student)
        return super().get_queryset()


class InstructorAnalyticsAPIView(APIView):
    """Read-only aggregate analytics for instructors and admin users."""

    permission_classes = [IsAuthenticated, IsAdminOrInstructorReadOnly]

    def get(self, request):
        return Response({
            "scope": "instructor",
            "summary": analytics_helpers.summary_stats(),
            "grade_distribution": analytics_helpers.grade_distribution(),
            "attendance_trend": analytics_helpers.attendance_trend(days=30),
            "course_average_scores": analytics_helpers.course_average_scores(),
            "enrollment_by_month": analytics_helpers.enrollment_by_month(),
            "course_enrollment_counts": analytics_helpers.course_enrollment_counts(),
            "module_average_scores": analytics_helpers.module_average_scores(),
            "top_students": analytics_helpers.top_performing_students(5),
            "bottom_students": analytics_helpers.bottom_performing_students(5),
        })


class StudentAnalyticsAPIView(APIView):
    """Read-only analytics restricted to the authenticated student."""

    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request):
        student = request.user.student
        result_queryset = Result.objects.filter(student=student).select_related("module")
        attendance_queryset = Attendance.objects.filter(student=student)

        return Response({
            "scope": "student",
            "student_id": student.id,
            "summary": analytics_helpers.summary_stats(result_queryset),
            "module_performance": analytics_helpers.student_module_performance(student),
            "grade_distribution": analytics_helpers.grade_distribution(result_queryset),
            "attendance_trend": analytics_helpers.attendance_trend(
                days=30,
                queryset=attendance_queryset,
            ),
            "grade_history": analytics_helpers.student_grade_history(student),
        })