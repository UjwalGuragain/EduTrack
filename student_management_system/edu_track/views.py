from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Course, Module, Student, Result, Attendance, Instructor
from .decorators import *

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
    
    instructor = request.user.instructor
    context = {
        "instructor" : instructor,
        "recent_students": Student.objects.order_by("-id")[:10],
        "student_count": Student.objects.count(),
        "course_count": Course.objects.count(),
        "module_count": Module.objects.count(),
        "result_count" : Result.objects.count(),
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

    context = {
        "present_count" : present_count,
        "absent_count" : absent_count,
        "attendance_percentage" : round(attendance_percentage, 2),
        "student" : student,
        "attendance" : attendance,
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
    context = {
        "average_marks": average_marks,
        "highest_marks" : highest_marks,
        "lowest_marks" : lowest_marks,
        "student" : student,
        "result" : result,
        "result_count" : result_count
    }
    return render(request, "edu_track/dashboards/my_result.html", context)

#CRUD OPERATIONS FOR COURSE
#Fetch all courses from Database and Send it to template
def list_courses(request):
    courses = Course.objects.all()
    return render(request, "edu_track/courses/course_list.html", {"courses": courses})

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
def list_students(request):
    students = Student.objects.all()
    return render(request, "edu_track/students/student_list.html", {"students": students})

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
def list_modules(request):
    module = Module.objects.all()
    return render(request, "edu_track/modules/module_list.html", {"modules" : module})

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
def list_result(request):
    result = Result.objects.all()
    return render(request, "edu_track/results/result_list.html", {"results" : result})

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
def list_attendance(request):
    attendance = Attendance.objects.all()
    return render(request, "edu_track/attendance/attendance_list.html", {"attendance" : attendance})

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