from django.shortcuts import render, redirect
from .models import Course, Module, Student, Result, Attendance

#CRUD OPERATIONS FOR COURSE
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

    duration_choices = Course.DURATION_CHOICES
    return render(request,"edu_track/courses/course_add.html", {"duration_choices": duration_choices},)

#Update courses
def course_update(request, id):
    course = Course.objects.get(id=id)

    if request.method == "POST":
        course.course_name = request.POST.get("course_name")
        course.course_duration = request.POST.get("course_duration")
        course.save()
        return redirect("course_list")

    duration_choices = Course.DURATION_CHOICES
    return render(request,"edu_track/courses/course_update.html",{"course": course, "duration_choices": duration_choices},)

#Delete courses
def course_delete(request, id):
    course = Course.objects.get(id=id)
    course.delete()
    return redirect("course_list")

# CRUD OPERATIONS FOR STUDENT
#Fetch all students from Database and Send it to template
def list_students(request):
    students = Student.objects.all()
    return render(request, "edu_track/students/student_list.html", {"students": students})

#Add new students
def student_add(request):
    courses = Course.objects.all()

    if request.method == "POST":
            full_name=request.POST.get("full_name"),
            address=request.POST.get("address"),
            contact_number=request.POST.get("contact_number"),
            email=request.POST.get("email"),
            guardian_name=request.POST.get("guardian_name"),
            enrollment_number=request.POST.get("enrollment_number"),
            enrolled_course=Course.objects.get(id=request.POST.get("enrolled_course")),
            enrollment_date=request.POST.get("enrollment_date")
        
            Student.objects.create(
                full_name = full_name,
                address = address,
                contact_number = contact_number,
                email = email,
                guardian_name = guardian_name,
                enrollment_number = enrollment_number,
                enrolled_course = enrolled_course,
                enrollment_date = enrollment_date,
            )

            return redirect("student_list")

    return render(request, "edu_track/students/student_add.html", {"courses": courses})

#Update students
def student_update(request, id):
    student = Student.objects.get(id=id)
    courses = Course.objects.all()

    if request.method == "POST":
        student.full_name = request.POST.get("full_name")
        student.address = request.POST.get("address")
        student.contact_number = request.POST.get("contact_number")
        student.email = request.POST.get("email")
        student.guardian_name = request.POST.get("guardian_name")
        student.enrollment_number = request.POST.get("enrollment_number")
        student.enrolled_course = Course.objects.get(id=request.POST.get("enrolled_course"))
        student.enrollment_date = request.POST.get("enrollment_date")
        student.save()
        return redirect("student_list")

    return render(request, "edu_track/students/student_update.html",{"student": student, "courses": courses})

#Delete students
def student_delete(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return redirect("student_list")