from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Course, Module, Student, Result, Attendance, Instructor
from .decorators import *
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import csv
from django.http import HttpResponse
from .forms import InstructorProfilePictureForm, StudentProfilePictureForm

#USER_LOGIN OPERATIONS
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  
        if hasattr(user, "student"):
            return redirect("student_dashboard")
        elif hasattr(user, "instructor"):
            return redirect("instructor_dashboard")
        else:
            messages.error(request, "Invalid credentials or Account not linked to Student or Instructor profile")
            return redirect("login")

    return render(request, "edu_track/registration/login.html")

#USER_REGISTER OPERATIONS
def user_register(request):
    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password1"]
        confirm_password = request.POST["password2"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")
        if len(password) < 9:
            messages.error(request, "Passwords must be of atleast 8 characters")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
       
        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "edu_track/registration/register.html")

#USER LOGOUT OPERATIONS
def user_logout(request):
    logout(request)
    return redirect("login")

#PASSWORD RESET OPERATIONS
def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email == email:
            messages.success(request, "Email sent successfully!")

    return render(request, "edu_track/registration/password_reset.html")

#RENDER INSTRUCTOR DASHBOARD
@instructor_required
def instructor_dashboard(request):
    if not hasattr(request.user,"instructor"):
        return redirect("login")
    
    present_count = Attendance.objects.filter(status = "Present").count()
    absent_count = Attendance.objects.filter(status = "Absent").count()
    total_attendance = Attendance.objects.count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    today = timezone.now().date()
    students_this_month = Student.objects.filter(
    enrollment_date__month=today.month,
    enrollment_date__year=today.year).count()

    attendance_today = Attendance.objects.filter(date=today).count()
    results_this_week = Result.objects.filter(id__isnull=False).order_by("-id")[:7].count()
    students_without_attendance = Student.objects.exclude(attendance__isnull=False).count()
    students_without_results = Student.objects.exclude(result__isnull=False).count()
    courses_without_modules = Course.objects.exclude(module__isnull=True).count()

    instructor = request.user.instructor
    context = {
        "instructor" : instructor,
        "recent_results" : Result.objects.order_by("-id")[:5],
        "recent_students": Student.objects.order_by("-id")[:5],
        "student_count": Student.objects.count(),
        "course_count": Course.objects.count(),
        "module_count": Module.objects.count(),
        "result_count" : Result.objects.count(),
        "present_count" : present_count,
        "absent_count" : absent_count,
        "recent_attendance" : Attendance.objects.order_by("-id")[:5],
        "attendance_percentage" : round(attendance_percentage, 2),
        "students_this_month": students_this_month,
        "attendance_today": attendance_today,
        "results_this_week": results_this_week,
        "students_without_attendance": students_without_attendance,
        "students_without_results": students_without_results,
        "courses_without_modules": courses_without_modules,
        
    }
    return render(request, "edu_track/dashboards/instructor_dashboard.html", context)

#RENDER STUDENT DASHBOARD
@student_required
def student_dashboard(request):
    if not hasattr(request.user,"student"):
        return redirect("login")
    
    student = request.user.student
    course = Course.objects.filter(student=student)
    result = Result.objects.filter(student=student).select_related("module")
    result_count = Result.objects.filter(student=student).count()
    attendance = Attendance.objects.filter(student=student).order_by("-date")
    present_count = Attendance.objects.filter(student=student).filter(status = "Present").count()
    absent_count = Attendance.objects.filter(student=student).filter(status = "Absent").count()
    total_attendance = Attendance.objects.filter(student=student).count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    context = {
        "enrolled_course" : course,
        "present_count" : present_count,
        "absent_count" : absent_count,
        "attendance_percentage" : round(attendance_percentage, 2),
        "recent_attendance" : attendance[:5],
        "student" : student,
        "result_count" : result_count,
        "recent_result" : result[:5]
    }
    return render(request, "edu_track/dashboards/student_dashboard.html", context)

#STUDENT PROFILE
@student_required
def my_profile(request):
    student = request.user.student

    context = {
        "student" : student
    }
    return render(request, "edu_track/dashboards/my_profile.html", context)

#STUDENT COURSE
@student_required
def my_course(request):
    student = request.user.student
    course = Course.objects.filter(student=student)

    context = {
        "student" : student,
        "enrolled_course" : course
    }
    return render(request, "edu_track/dashboards/my_course.html", context)

#STUDENT MOUDLE
@student_required
def my_module(request):
    student = request.user.student
    module = Result.objects.filter(student=student).select_related("module")

    context = {
        "student" : student,
        "module" : module
    }
    return render(request, "edu_track/dashboards/my_module.html", context)

#STUDENT ATTENDANCE
@student_required
def my_attendance(request):
    student = request.user.student
    attendance = Attendance.objects.filter(student=student)
    present_count = Attendance.objects.filter(student=student).filter(status = "Present").count()
    absent_count = Attendance.objects.filter(student=student).filter(status = "Absent").count()
    total_attendance = Attendance.objects.filter(student=student).count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )
    paginator = Paginator(attendance, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "present_count" : present_count,
        "absent_count" : absent_count,
        "attendance_percentage" : round(attendance_percentage, 2),
        "student" : student,
        "attendance" : page_obj,
        "page_obj" : page_obj,
        "total_attendance" : total_attendance
    }
    return render(request, "edu_track/dashboards/my_attendance.html", context)

#STUDENT RESULT
@student_required
def my_result(request):
    student = request.user.student
    result = Result.objects.filter(student=student).select_related("module")
    marks = [float(r.obtained_marks) for r in result]
    average_marks = (
        round(sum(marks) / len(marks), 2)
        if marks else 0
    )
    highest_marks = max(marks) if marks else 0
    lowest_marks = min(marks) if marks else 0
    result_count = result.count()

    paginator = Paginator(result, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "average_marks": average_marks,
        "highest_marks" : highest_marks,
        "lowest_marks" : lowest_marks,
        "student" : student,
        "result" : page_obj,
        "page_obj" : page_obj,
        "result_count" : result_count
    }
    return render(request, "edu_track/dashboards/my_result.html", context)

#Display overall details of the student
@instructor_required
def student_detail(request, id):
    student = Student.objects.get(id=id)
    attendance = Attendance.objects.filter(student=student)
    result = Result.objects.filter(student=student).select_related("module")
    present_count = attendance.filter(status = "Present").count()
    absent_count = attendance.filter(status = "Absent").count()
    total_attendance = attendance.count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    context = {
        "student" : student,
        "result" : result,
        "attendance" : attendance,
        "present_count" : present_count,
        "absent_count" : absent_count,
        "attendance_percentage" : round(attendance_percentage, 2)
    }

    return render(request, "edu_track/students/student_detail.html", context)
#CRUD OPERATIONS FOR COURSE
#Fetch all courses from Database and Send it to template
@instructor_required
def list_courses(request):
    courses = Course.objects.all()
    paginator = Paginator(courses, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "courses" : page_obj,
        "page_obj" : page_obj
    }

    return render(request, "edu_track/courses/course_list.html", context)

#Add new courses
@instructor_required
def course_add(request):
    print(request.user)
    if request.method == "POST":
        code = request.POST.get("course_code")
        name = request.POST.get("course_name")
        duration = request.POST.get("course_duration")

        Course.objects.create(
            course_code = code,
            course_name=name,
            course_duration=duration
        )
        return redirect("course_list")

    duration_choices = Course.DURATION_CHOICES
    return render(request,"edu_track/courses/course_add.html", {"duration_choices": duration_choices},)

#Update courses
@instructor_required
def course_update(request, id):
    course = Course.objects.get(id=id)

    if request.method == "POST":
        course.course_code = request.POST.get("course_code")
        course.course_name = request.POST.get("course_name")
        course.course_duration = request.POST.get("course_duration")
        course.save()
        return redirect("course_list")

    duration_choices = Course.DURATION_CHOICES
    return render(request,"edu_track/courses/course_update.html",{"course": course, "duration_choices": duration_choices},)

#Delete courses
@instructor_required
def course_delete(request, id):
    course = Course.objects.get(id=id)
    course.delete()
    return redirect("course_list")

# CRUD OPERATIONS FOR STUDENT
#Fetch all students from Database and Send it to template
@instructor_required
def list_students(request):
    search = request.GET.get("search", "")
    students = Student.objects.all()
    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if search:
        students = students.filter(
        Q(full_name__icontains = search) | 
        Q(email__icontains = search) |
        Q(enrollment_number__icontains = search)
        )

    context = {
            "students" : page_obj,
            "search" : search
        }
    return render(request, "edu_track/students/student_list.html", context)

#Add new students
@instructor_required
def student_add(request):
    users = User.objects.filter(student__isnull=True)
    courses = Course.objects.all()

    if request.method == "POST":
            user = User.objects.get(id=request.POST.get("user"))
            full_name=request.POST.get("full_name")
            address=request.POST.get("address")
            contact_number=request.POST.get("contact_number")
            email=request.POST.get("email")
            guardian_name=request.POST.get("guardian_name")
            enrollment_number=request.POST.get("enrollment_number")
            enrolled_course=Course.objects.get(id=request.POST.get("enrolled_course"))
            enrollment_date=request.POST.get("enrollment_date")
        
            Student.objects.create(
                user = user,
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

    return render(request, "edu_track/students/student_add.html", {"courses": courses, "users": users})

#Update students
@instructor_required
def student_update(request, id):
    users = User.objects.filter(student__isnull=True)
    student = Student.objects.get(id=id)
    courses = Course.objects.all()

    if request.method == "POST":
        student.user = User.objects.get(id=request.POST.get("user"))
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

    return render(request, "edu_track/students/student_update.html",{"student": student, "courses": courses, "users" : users})

#Delete students
@instructor_required
def student_delete(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return redirect("student_list")

#CRUD OPERATIONS FOR MODULE
#Fetch all modules from Database and Sent it to template
@instructor_required
def list_modules(request):
    module = Module.objects.all()
    paginator = Paginator(module, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "modules" : page_obj,
        "page_obj" : page_obj
    }
    return render(request, "edu_track/modules/module_list.html", context)

#Add modules
@instructor_required
def module_add(request):
    course = Course.objects.all()
    if request.method == "POST":
        module_name = request.POST.get("module_name")
        module_code = request.POST.get("mdoule_code")
        full_marks = request.POST.get("full_marks")
        courses = Course.objects.get(id = request.POST.get("courses"))

        Module.objects.create(
            module_name = module_name,
            mdoule_code = module_code,
            full_marks = full_marks,
            courses = courses
        )

        return redirect("module_list")
    return render(request,"edu_track/modules/module_add.html", {"courses" : course} )

#Update modules
@instructor_required
def module_update(request, id):
    module = Module.objects.get(id = id)
    course = Course.objects.all()

    if request.method == "POST":
        module.module_name = request.POST.get("module_name")
        module.module_code = request.POST.get("module_code")
        module.full_marks = request.POST.get("full_marks")
        module.courses = Course.objects.get(id=request.POST.get("courses"))
        module.save()
        return redirect("module_list")
    
    return render(request, "edu_track/modules/module_update.html", {"module" : module, "courses" : course})

#Delete modules
@instructor_required
def module_delete(request, id):
    module = Module.objects.get(id = id)
    module.delete()
    return redirect("module_list")

#CRUD OPERATIONS FOR RESULT
#Fetch results from Database and Send it to template
@instructor_required
def list_result(request):
    search = request.GET.get("search", "")
    result = Result.objects.all()
    paginator = Paginator(result, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    
    if search:
        result = result.filter(
        Q(student__full_name__icontains = search) |
        Q(module__module_name__icontains = search)
        )

    context = {
        "results" : page_obj,
        "page_obj" : page_obj,
        "search" : search
    }
    return render(request, "edu_track/results/result_list.html", context)

#Add Results
@instructor_required
def result_add(request):
    student = Student.objects.all()
    module  = Module.objects.all()

    if request.method == "POST":
        student = Student.objects.get(id = request.POST.get("student"))
        module = Module.objects.get(id = request.POST.get("module"))
        obtained_marks = request.POST.get("obtained_marks")

        Result.objects.create(
            student = student,
            module = module,
            obtained_marks = obtained_marks
        )
        
        return redirect("result_list")
    return render(request, "edu_track/results/result_add.html", {"student": student, "modules" : module})

#Update Result
@instructor_required
def result_update(request, id):
    result = Result.objects.get(id = id)
    module = Module.objects.all()
    student = Student.objects.all()
    if request.method == "POST":
        result.student = Student.objects.get(id = request.POST.get("student"))
        result.module = Module.objects.get(id = request.POST.get("module"))
        result.obtained_marks = request.POST.get("obtained_marks")
        result.save()
        return redirect("result_list")
    return render(request, "edu_track/results/result_update.html", {"modules" : module, "students": student, "results" : result})

#Delete Result
@instructor_required
def result_delete(request, id):
    result = Result.objects.get(id = id)
    result.delete()
    return redirect("result_list")

#CRUD OPERATIONS FOR ATTENDANCE
# Fetch all attendances from Database and Send it to template
@instructor_required
def list_attendance(request):
    search = request.GET.get("search", "")
    attendance = Attendance.objects.all()
    paginator = Paginator(attendance, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    if search:
        attendance = attendance.filter(
            Q(student__full_name__icontains = search)
        )
    context = {
        "attendance" : page_obj,
        "page_obj" : page_obj,
        "search" : search
    }
    return render(request, "edu_track/attendance/attendance_list.html", context)

#Add attendance
@instructor_required
def attendance_add(request):
    student = Student.objects.all()

    if request.method == "POST":
        student = Student.objects.get(id = request.POST.get("student"))
        date = request.POST.get("date")
        status = request.POST.get("status")

        Attendance.objects.create(
            student = Student.objects.get(id = request.POST.get("student")),
            date = date,
            status = status
        )
        return redirect("attendance_list")
    status_choices = Attendance.STATUS_CHOICES
    return render(request, "edu_track/attendance/attendance_add.html", {"student" : student, "status_choices" : status_choices})

#Update attendance
@instructor_required
def attendance_update(request, id):
    attendance = Attendance.objects.get(id = id)
    student = Student.objects.all()

    if request.method == "POST":
        attendance.student = Student.objects.get(id = request.POST.get("student"))
        attendance.date = request.POST.get("date")
        attendance.status = request.POST.get("status")
        attendance.save()
        return redirect("attendance_list")
    
    status_duration = Attendance.STATUS_CHOICES
    return render(request, "edu_track/attendance/attendance_update.html", {"student" : student, "attendance" : attendance})

#Delete attendance
@instructor_required
def attendance_delete(request, id):
    attendance = Attendance.objects.get(id = id)
    attendance.delete()
    return redirect("attendance_list")

#EXPORT STUDENT LIST AS CSV
@instructor_required
def student_export_csv(request):
    response = HttpResponse(content_type = "text/csv")
    response["Content-Disposition"] = 'attachment; filename = "Edutrack Students.csv"'

    writer = csv.writer(response)
    writer.writerow(["Full Name", "Address", "Contact Number", "Email", "Guardian Name", "Enrollment Number", "Enrolled Course", "Enrollment Date"])
    students = Student.objects.select_related("enrolled_course")
    for student in students:
        writer.writerow([student.full_name, student.address, student.contact_number, student.email, student.guardian_name, student.enrollment_number, student.enrolled_course, student.enrollment_date])
    return response

#IMPORT STUDENT LIST FROM CSV
@instructor_required
def student_import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Please select a CSV File.")
            return redirect("student_import_csv")
        
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        imported = 0

        for row in reader:
            course = Course.objects.get(course_name = row ['Enrolled Course'])
            Student.objects.create(
                full_name = row ['Full Name'],
                address = row ['Address'],
                contact_number = row ['Contact Number'],
                email = row ['Email'],
                guardian_name = row ['Guardian Name'],
                enrollment_number = row ['Enrollment Number'],
                enrolled_course = course,
                enrollment_date = row ['Enrollment Date']
            )

            imported += 1

        messages.success(request, f"{imported} students imported successfully.")
        return redirect("student_list")
    
    return render(request, "edu_track/students/import_students_csv.html")

#INSTRUCTOR PROFILE
def instructor_profile(request):
    instructor = request.user.instructor

    context = {
        "instructor": instructor,
    }

    return render(
        request,
        "edu_track/dashboards/instructor_profile.html",
        context,
    )

