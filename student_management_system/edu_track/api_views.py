from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import (
    IsAdminOrInstructorReadOnly,
    IsAdminOrInstructorWrite,
    IsAdminOrStudentReadOnly,
    IsAttendanceStudentOwnerOrReadOnly,
    IsResultStudentOwnerOrReadOnly,
    IsStudentOwnerOrReadOnly,
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