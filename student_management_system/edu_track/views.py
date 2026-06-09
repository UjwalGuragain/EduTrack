from django.shortcuts import render, redirect
from .models import Course, Module, Student, Result, Attendance

#Fetch all courses from Database and Send it to template
def list_courses(request):
    courses = Course.objects.all()
    return render(request, "edu_track/courses/course_list.html", {"courses": courses})

#Add new courses
def course_add(request):
    if request.method == "POST":
        name = request.POST.get("course_name")
        duration = request.POST.get("course_duration")

        Course.objects.create(
            course_name=name,
            course_duration=duration
        )
        return redirect("course_list")

    return render(request, "edu_track/courses/course_add.html")

#Update courses
def course_update(request, id):
    course = Course.objects.get(id=id)

    if request.method == "POST":
        course.course_name = request.POST.get("course_name")
        course.course_duration = request.POST.get("course_duration")
        course.save()
        return redirect("course_list")

    return render(request, "edu_track/courses/course_update.html", {"course": course})

#Delete courses
def course_delete(request, id):
    course = Course.objects.get(id=id)
    course.delete()
    return redirect("course_list")