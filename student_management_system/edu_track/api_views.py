from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from rest_framework import status
from django.shortcuts import get_object_or_404

@api_view(["GET", "POST"])
def student_api(request):
    
    if request.method == "GET":

        students = Student.objects.all()
        serializer = StudentSerializer(students, many = True)
       
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "POST":

        serializer = StudentSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def instructor_api(request):

    if request.method == "GET":

        instructors = Instructor.objects.all()
        serializer = InstructorSerializer(instructors, many = True)

        return Response(serializer.data, staus = status.HTTP_200_OK)

    elif request.method == "POST":

        serializer = InstructorSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
   
@api_view(["GET", "POST"])
def course_api(request):

    if request.method == "GET":

        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "POST":

        serializer = CourseSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def module_api(request):

    if request.method == "GET":
        
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "POST":

        serializer = ModuleSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def attendance_api(request):

    if request.method == "GET":

        attendances = Attendance.objects.all()
        serializer = AttendanceSerializer(attendances, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "POST":

        serializer = AttendanceSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def result_api(request):

    if request.method == "GET":

        results = Result.objects.all()
        serializer = ResultSerializer(results, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "POST":

        serializer = ResultSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def student_detail_api(request, id):

    student = get_object_or_404(Student, id=id)

    if request.method == "GET":

        serializer = StudentSerializer(student, many = False)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "PATCH":

        serializer = StudentSerializer(student, data = request.data, partial = True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":

        serializer = StudentSerializer(student, data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
    elif request.method == "DELETE":
        student.delete()

        return Response(status = status.HTTP_204_NO_CONTENT)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def module_detail_api(request, id):

    module = get_object_or_404(Module, id=id)

    if request.method == "GET":

        serializer = ModuleSerializer(module, many = False)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method == "PATCH":

        serializer = ModuleSerializer(module, data = request.data, partial = True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":

        serializer = ModuleSerializer(module, data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
    elif request.method == "DELETE":
        module.delete()

        return Response(status = status.HTTP_204_NO_CONTENT)
    