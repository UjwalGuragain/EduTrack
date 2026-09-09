from django.shortcuts import render, redirect, get_object_or_404
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
from datetime import date
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Spacer, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def grade_for_percentage(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B+"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"


def result_percentage(result):
    full_marks = float(result.module.full_marks)
    if full_marks <= 0:
        return 0
    return round((float(result.obtained_marks) / full_marks) * 100, 2)


#USER_LOGIN OPERATIONS
def user_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "student"):
            return redirect("student_dashboard")
        elif hasattr(request.user, "instructor"):
            return redirect("instructor_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  
            if hasattr(user, "student"):
                return redirect("student_dashboard")
            elif hasattr(user, "instructor"):
                return redirect("instructor_dashboard")
            else:
                messages.warning(request, "Account is not linked to a Student or Instructor profile.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "edu_track/registration/login.html")

#USER_REGISTER OPERATIONS
def user_register(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "student"):
            return redirect("student_dashboard")
        elif hasattr(request.user, "instructor"):
            return redirect("instructor_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password1", "")
        confirm_password = request.POST.get("password2", "")

        if not username:
            messages.error(request, "Username is required.")
            return redirect("register")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if len(password) < 8:
            messages.error(request, "Passwords must be at least 8 characters.")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
       
        messages.success(request, "Account created successfully! Please sign in.")
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
    if not hasattr(request.user, "instructor") and not request.user.is_staff:
        return redirect("login")

    present_count = Attendance.objects.filter(status="Present").count()
    absent_count = Attendance.objects.filter(status="Absent").count()
    total_attendance = Attendance.objects.count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    today = timezone.now().date()
    students_this_month = Student.objects.filter(
        enrollment_date__month=today.month,
        enrollment_date__year=today.year
    ).count()

    attendance_today = Attendance.objects.filter(date=today).count()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    attendance_this_week = Attendance.objects.filter(date__gte=start_of_week, date__lte=today).count()
    results_this_week = Result.objects.count()
    students_without_attendance = Student.objects.filter(attendance__isnull=True).distinct().count()
    students_without_results = Student.objects.filter(result__isnull=True).distinct().count()
    courses_without_modules = Course.objects.filter(module__isnull=True).distinct().count()

    instructor = getattr(request.user, "instructor", None)
    context = {
        "instructor": instructor,
        "recent_results": Result.objects.select_related("student", "module").order_by("-id")[:5],
        "recent_students": Student.objects.select_related("enrolled_course").order_by("-id")[:5],
        "student_count": Student.objects.count(),
        "course_count": Course.objects.count(),
        "module_count": Module.objects.count(),
        "result_count": Result.objects.count(),
        "present_count": present_count,
        "absent_count": absent_count,
        "recent_attendance": Attendance.objects.select_related("student").order_by("-date", "-id")[:5],
        "attendance_percentage": round(attendance_percentage, 2),
        "students_this_month": students_this_month,
        "attendance_today": attendance_today,
        "attendance_this_week": attendance_this_week,
        "results_this_week": results_this_week,
        "students_without_attendance": students_without_attendance,
        "students_without_results": students_without_results,
        "courses_without_modules": courses_without_modules,
    }
    return render(request, "edu_track/dashboards/instructor_dashboard.html", context)

#RENDER STUDENT DASHBOARD
@student_required
def student_dashboard(request):
    if not hasattr(request.user, "student"):
        return redirect("login")
    
    student = request.user.student
    course = Course.objects.filter(id=student.enrolled_course_id) if student.enrolled_course else Course.objects.none()
    result = Result.objects.filter(student=student).select_related("module").order_by("-id")
    result_count = Result.objects.filter(student=student).count()
    attendance = Attendance.objects.filter(student=student).order_by("-date", "-id")
    present_count = Attendance.objects.filter(student=student, status="Present").count()
    absent_count = Attendance.objects.filter(student=student, status="Absent").count()
    total_attendance = Attendance.objects.filter(student=student).count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    context = {
        "enrolled_course": course,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": round(attendance_percentage, 2),
        "recent_attendance": attendance[:5],
        "student": student,
        "result_count": result_count,
        "recent_result": result[:5]
    }
    return render(request, "edu_track/dashboards/student_dashboard.html", context)

#STUDENT PROFILE
@student_required
def student_profile(request):
    student = request.user.student

    context = {
        "student": student
    }
    return render(request, "edu_track/dashboards/my_profile.html", context)

#STUDENT COURSE
@student_required
def student_course(request):
    student = request.user.student
    course = Course.objects.filter(id=student.enrolled_course_id) if student.enrolled_course else Course.objects.none()

    context = {
        "student": student,
        "enrolled_course": course
    }
    return render(request, "edu_track/dashboards/my_course.html", context)

#STUDENT MODULE
@student_required
def student_module(request):
    student = request.user.student
    modules = Module.objects.filter(courses=student.enrolled_course).select_related("courses").order_by("module_code") if student.enrolled_course else Module.objects.none()

    context = {
        "student": student,
        "modules": modules,
        "module": modules,
    }
    return render(request, "edu_track/dashboards/my_module.html", context)

#STUDENT ATTENDANCE
@student_required
def student_attendance(request):
    student = request.user.student
    attendance = Attendance.objects.filter(student=student).order_by("-date", "-id")
    present_count = attendance.filter(status="Present").count()
    absent_count = attendance.filter(status="Absent").count()
    total_attendance = attendance.count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )
    paginator = Paginator(attendance, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": round(attendance_percentage, 2),
        "student": student,
        "attendance": page_obj,
        "page_obj": page_obj,
        "total_attendance": total_attendance
    }
    return render(request, "edu_track/dashboards/my_attendance.html", context)

#STUDENT RESULT
@student_required
def student_result(request):
    student = request.user.student
    result = Result.objects.filter(student=student).select_related("module").order_by("module__module_name", "id")
    marks = [float(r.obtained_marks) for r in result]
    average_marks = (
        round(sum(marks) / len(marks), 2)
        if marks else 0
    )
    highest_marks = max(marks) if marks else 0
    lowest_marks = min(marks) if marks else 0
    result_count = result.count()
    total_full_marks = sum(float(r.module.full_marks) for r in result)
    total_obtained_marks = sum(marks)
    overall_percentage = (
        round((total_obtained_marks / total_full_marks) * 100, 2)
        if total_full_marks else 0
    )

    paginator = Paginator(result, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    for result_item in page_obj:
        result_item.percentage = result_percentage(result_item)
        result_item.grade = grade_for_percentage(result_item.percentage)

    context = {
        "average_marks": average_marks,
        "highest_marks": highest_marks,
        "lowest_marks": lowest_marks,
        "overall_percentage": overall_percentage,
        "overall_grade": grade_for_percentage(overall_percentage),
        "student": student,
        "result": page_obj,
        "page_obj": page_obj,
        "result_count": result_count
    }
    return render(request, "edu_track/dashboards/my_result.html", context)

#Display overall details of the student
@admin_or_instructor_required
def student_detail(request, id):
    student = get_object_or_404(Student.objects.select_related("enrolled_course", "user"), id=id)
    attendance = Attendance.objects.filter(student=student).order_by("-date", "-id")
    result = Result.objects.filter(student=student).select_related("module").order_by("module__module_name", "id")
    present_count = attendance.filter(status="Present").count()
    absent_count = attendance.filter(status="Absent").count()
    total_attendance = attendance.count()
    attendance_percentage = (
        (present_count / total_attendance) * 100
        if total_attendance else 0
    )

    context = {
        "student": student,
        "result": result,
        "attendance": attendance,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": round(attendance_percentage, 2)
    }

    return render(request, "edu_track/students/student_detail.html", context)

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
@admin_or_instructor_required
def list_courses(request):
    courses = Course.objects.all().order_by("id")
    paginator = Paginator(courses, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "courses" : page_obj,
        "page_obj" : page_obj
    }

    return render(request, "edu_track/courses/course_list.html", context)

#Add new courses
@admin_or_instructor_required
def course_add(request):
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
@admin_or_instructor_required
def course_update(request, id):
    course = get_object_or_404(Course, id=id)

    if request.method == "POST":
        course.course_code = request.POST.get("course_code")
        course.course_name = request.POST.get("course_name")
        course.course_duration = request.POST.get("course_duration")
        course.save()
        return redirect("course_list")

    duration_choices = Course.DURATION_CHOICES
    return render(request,"edu_track/courses/course_update.html",{"course": course, "duration_choices": duration_choices},)

#Delete courses
@admin_or_instructor_required
def course_delete(request, id):
    course = get_object_or_404(Course, id=id)
    course.delete()
    return redirect("course_list")

# CRUD OPERATIONS FOR STUDENT
#Fetch all students from Database and Send it to template
@admin_or_instructor_required
def list_students(request):
    search = request.GET.get("search", "")
    students = Student.objects.select_related("enrolled_course", "user").order_by("id")

    if search:
        students = students.filter(
            Q(full_name__icontains = search) | 
            Q(email__icontains = search) |
            Q(enrollment_number__icontains = search) |
            Q(enrolled_course__course_name__icontains = search)
        )

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "students" : page_obj,
        "page_obj" : page_obj,
        "search" : search
    }
    return render(request, "edu_track/students/student_list.html", context)

#Add new students
@admin_or_instructor_required
def student_add(request):
    users = User.objects.filter(student__isnull=True, instructor__isnull=True, is_superuser=False)
    courses = Course.objects.all()

    if request.method == "POST":
        user_id = request.POST.get("user")
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                user = None

        full_name = request.POST.get("full_name")
        address = request.POST.get("address")
        contact_number = request.POST.get("contact_number")
        email = request.POST.get("email")
        guardian_name = request.POST.get("guardian_name")
        enrollment_number = request.POST.get("enrollment_number")
        enrolled_course = get_object_or_404(Course, id=request.POST.get("enrolled_course"))
        enrollment_date = request.POST.get("enrollment_date")
    
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
@admin_or_instructor_required
def student_update(request, id):
    student = get_object_or_404(Student, id=id)
    users = User.objects.filter(
        Q(student__isnull=True, instructor__isnull=True, is_superuser=False) |
        Q(id=student.user.id if student.user else None)
    ).distinct()
    courses = Course.objects.all()

    if request.method == "POST":
        user_id = request.POST.get("user")
        if user_id:
            try:
                student.user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                student.user = None
        else:
            student.user = None

        student.full_name = request.POST.get("full_name")
        student.address = request.POST.get("address")
        student.contact_number = request.POST.get("contact_number")
        student.email = request.POST.get("email")
        student.guardian_name = request.POST.get("guardian_name")
        student.enrollment_number = request.POST.get("enrollment_number")
        student.enrolled_course = get_object_or_404(Course, id=request.POST.get("enrolled_course"))
        student.enrollment_date = request.POST.get("enrollment_date")
        student.save()
        return redirect("student_list")

    return render(request, "edu_track/students/student_update.html", {"student": student, "courses": courses, "users": users})

#Delete students
@admin_or_instructor_required
def student_delete(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect("student_list")

# CRUD OPERATIONS FOR INSTRUCTOR
@admin_or_instructor_required
def list_instructors(request):
    search = request.GET.get("search", "")
    instructors = Instructor.objects.select_related("user").order_by("id")

    if search:
        instructors = instructors.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(qualification__icontains=search)
        )

    paginator = Paginator(instructors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "instructors": page_obj,
        "page_obj": page_obj,
        "search": search,
        "can_manage_instructors": request.user.is_staff,
    }
    return render(request, "edu_track/instructors/instructor_list.html", context)

@admin_or_staff_required
def instructor_add(request):
    if not request.user.is_staff:
        messages.error(request, "Only admins can add new instructors.")
        return redirect("instructor_dashboard")

    users = User.objects.filter(student__isnull=True, instructor__isnull=True, is_superuser=False)

    if request.method == "POST":
        user_id = request.POST.get("user")
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                user = None

        Instructor.objects.create(
            user=user,
            full_name=request.POST.get("full_name"),
            contact_number=request.POST.get("contact_number"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
            qualification=request.POST.get("qualification"),
        )
        return redirect("instructor_list")

    return render(request, "edu_track/instructors/instructor_add.html", {"users": users})

@admin_or_instructor_required
def instructor_update(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    if not request.user.is_staff and request.user.instructor.id != instructor.id:
        messages.error(request, "You can only edit your own instructor profile.")
        return redirect("instructor_dashboard")

    users = User.objects.filter(
        Q(student__isnull=True, instructor__isnull=True, is_superuser=False) |
        Q(id=instructor.user.id if instructor.user else None)
    ).distinct()

    if request.method == "POST":
        if not request.user.is_staff and request.user.instructor.id != instructor.id:
            messages.error(request, "You can only edit your own instructor profile.")
            return redirect("instructor_dashboard")

        user_id = request.POST.get("user")
        if user_id:
            try:
                instructor.user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                instructor.user = None
        else:
            instructor.user = None

        instructor.full_name = request.POST.get("full_name")
        instructor.contact_number = request.POST.get("contact_number")
        instructor.email = request.POST.get("email")
        instructor.address = request.POST.get("address")
        instructor.qualification = request.POST.get("qualification")
        instructor.save()
        return redirect("instructor_list")

    return render(
        request,
        "edu_track/instructors/instructor_update.html",
        {"instructor": instructor, "users": users, "can_manage_instructors": request.user.is_staff},
    )

@admin_or_staff_required
def instructor_delete(request, id):
    if not request.user.is_staff:
        messages.error(request, "Only admins can delete instructors.")
        return redirect("instructor_dashboard")

    instructor = get_object_or_404(Instructor, id=id)
    instructor.delete()
    return redirect("instructor_list")

#CRUD OPERATIONS FOR MODULE
#Fetch all modules from Database and Sent it to template
@admin_or_instructor_required
def list_modules(request):
    modules = Module.objects.select_related("courses").order_by("id")
    paginator = Paginator(modules, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "modules": page_obj,
        "page_obj": page_obj
    }
    return render(request, "edu_track/modules/module_list.html", context)

#Add modules
@admin_or_instructor_required
def module_add(request):
    course = Course.objects.all()
    if request.method == "POST":
        module_name = request.POST.get("module_name")
        module_code = request.POST.get("module_code")
        full_marks = request.POST.get("full_marks")
        courses = get_object_or_404(Course, id = request.POST.get("courses"))

        Module.objects.create(
            module_name = module_name,
            module_code = module_code,
            full_marks = full_marks,
            courses = courses
        )

        return redirect("module_list")
    return render(request,"edu_track/modules/module_add.html", {"courses" : course} )

#Update modules
@admin_or_instructor_required
def module_update(request, id):
    module = get_object_or_404(Module, id = id)
    course = Course.objects.all()

    if request.method == "POST":
        module.module_name = request.POST.get("module_name")
        module.module_code = request.POST.get("module_code")
        module.full_marks = request.POST.get("full_marks")
        module.courses = get_object_or_404(Course, id = request.POST.get("courses"))
        module.save()
        return redirect("module_list")
    
    return render(request, "edu_track/modules/module_update.html", {"module" : module, "courses" : course})

#Delete modules
@admin_or_instructor_required
def module_delete(request, id):
    module = get_object_or_404(Module, id = id)
    module.delete()
    return redirect("module_list")

#CRUD OPERATIONS FOR RESULT
#Fetch results from Database and Send it to template
@admin_or_instructor_required
def list_result(request):
    search = request.GET.get("search", "")
    result = Result.objects.select_related("student", "module").order_by("id")
    
    if search:
        result = result.filter(
            Q(student__full_name__icontains = search) |
            Q(module__module_name__icontains = search)
        )

    paginator = Paginator(result, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "results" : page_obj,
        "page_obj" : page_obj,
        "search" : search
    }
    return render(request, "edu_track/results/result_list.html", context)

#Add Results
@admin_or_instructor_required
def result_add(request):
    student = Student.objects.all()
    module  = Module.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student")
        module_id = request.POST.get("module")
        obtained_marks = request.POST.get("obtained_marks")

        student_obj = get_object_or_404(Student, id=student_id)
        module_obj = get_object_or_404(Module, id=module_id)

        Result.objects.create(
            student = student_obj,
            module = module_obj,
            obtained_marks = obtained_marks
        )
        
        return redirect("result_list")
    return render(request, "edu_track/results/result_add.html", {"student": student, "modules" : module})

#Update Result
@admin_or_instructor_required
def result_update(request, id):
    result = get_object_or_404(Result, id=id)
    module = Module.objects.all()
    student = Student.objects.all()
    if request.method == "POST":
        result.student = get_object_or_404(Student, id=request.POST.get("student"))
        result.module = get_object_or_404(Module, id=request.POST.get("module"))
        result.obtained_marks = request.POST.get("obtained_marks")
        result.save()
        return redirect("result_list")
    return render(request, "edu_track/results/result_update.html", {"modules" : module, "students": student, "results" : result})

#Delete Result
@admin_or_instructor_required
def result_delete(request, id):
    result = get_object_or_404(Result, id=id)
    result.delete()
    return redirect("result_list")

#CRUD OPERATIONS FOR ATTENDANCE
# Fetch all attendances from Database and Send it to template
@admin_or_instructor_required
def list_attendance(request):
    search = request.GET.get("search", "")
    attendance = Attendance.objects.select_related("student").order_by("-date", "-id")
    
    if search:
        attendance = attendance.filter(
            Q(student__full_name__icontains = search)
        )

    paginator = Paginator(attendance, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "attendance" : page_obj,
        "page_obj" : page_obj,
        "search" : search
    }
    return render(request, "edu_track/attendance/attendance_list.html", context)

#Add attendance
@admin_or_instructor_required
def attendance_add(request):
    student = Student.objects.all()

    if request.method == "POST":
        student_obj = get_object_or_404(Student, id=request.POST.get("student"))
        date = request.POST.get("date")
        status = request.POST.get("status")

        Attendance.objects.create(
            student = student_obj,
            date = date,
            status = status
        )
        return redirect("attendance_list")
    status_choices = Attendance.STATUS_CHOICES
    return render(request, "edu_track/attendance/attendance_add.html", {"student" : student, "status_choices" : status_choices})

#Update attendance
@admin_or_instructor_required
def attendance_update(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    student = Student.objects.all()

    if request.method == "POST":
        attendance.student = get_object_or_404(Student, id=request.POST.get("student"))
        attendance.date = request.POST.get("date")
        attendance.status = request.POST.get("status")
        attendance.save()
        return redirect("attendance_list")
    
    status_duration = Attendance.STATUS_CHOICES
    return render(request, "edu_track/attendance/attendance_update.html", {"student" : student, "attendance" : attendance})

#Delete attendance
@admin_or_instructor_required
def attendance_delete(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    attendance.delete()
    return redirect("attendance_list")

#EXPORT STUDENT LIST AS CSV
@admin_or_instructor_required
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
@admin_or_instructor_required
def student_import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Please select a CSV File.")
            return redirect("student_import_csv")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid CSV file (.csv).")
            return redirect("student_import_csv")
        
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
        except Exception as e:
            messages.error(request, f"Error reading CSV file: {str(e)}")
            return redirect("student_import_csv")

        imported = 0
        errors = []

        for row_number, row in enumerate(reader, start=2):
            course_name = row.get("Enrolled Course", "").strip() if row.get("Enrolled Course") else ""
            if not course_name:
                errors.append(f"Row {row_number}: Course name is required.")
                continue

            try:
                course = Course.objects.get(course_name__iexact=course_name)
            except Course.DoesNotExist:
                errors.append(f"Row {row_number}: Course '{course_name}' does not exist.")
                continue
            except Course.MultipleObjectsReturned:
                course = Course.objects.filter(course_name__iexact=course_name).first()

            enrollment_number = row.get("Enrollment Number", "").strip() if row.get("Enrollment Number") else ""
            if not enrollment_number:
                errors.append(f"Row {row_number}: Enrollment number is required.")
                continue

            if Student.objects.filter(enrollment_number=enrollment_number).exists():
                errors.append(f"Row {row_number}: Enrollment number '{enrollment_number}' already exists.")
                continue

            try:
                Student.objects.create(
                    full_name = row.get("Full Name", "").strip(),
                    address = row.get("Address", "").strip(),
                    contact_number = row.get("Contact Number", "").strip(),
                    email = row.get("Email", "").strip(),
                    guardian_name = row.get("Guardian Name", "").strip(),
                    enrollment_number = enrollment_number,
                    enrolled_course = course,
                    enrollment_date = row.get("Enrollment Date", "").strip()
                )
                imported += 1
            except Exception as e:
                errors.append(f"Row {row_number}: {str(e)}")

        if imported > 0:
            messages.success(request, f"{imported} student(s) imported successfully.")
        if errors:
            messages.warning(request, f"Some records could not be imported: {'; '.join(errors[:5])}" + (f" (and {len(errors)-5} more errors)" if len(errors) > 5 else ""))
        if imported == 0 and errors:
            return redirect("student_import_csv")
        return redirect("student_list")
    
    return render(request, "edu_track/students/import_students_csv.html")

#INSTRUCTOR PROFILE
@instructor_required
def instructor_profile(request):
    instructor = getattr(request.user, "instructor", None)
    if not instructor:
        messages.error(request, "Only instructor profiles can view this page.")
        return redirect("instructor_dashboard")

    context = {
        "instructor": instructor,
    }

    return render(
        request,
        "edu_track/dashboards/instructor_profile.html",
        context,
    )

#UPLOAD STUDENT PROFILE PICTURE
@student_required
def student_upload_picture(request):
    student = request.user.student

    if request.method == "POST":
        form = StudentProfilePictureForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("student_profile")

    else:
        form = StudentProfilePictureForm(instance=student)

    return render(request, "profile_picture_upload.html", {"form": form, "picture": student.profile_picture} )

#UPLOAD INSTRUCTOR PROFILE PICTURE
@instructor_required
def instructor_upload_picture(request):
    instructor = getattr(request.user, "instructor", None)
    if not instructor:
        messages.error(request, "Only instructor profiles can upload a profile picture.")
        return redirect("instructor_dashboard")

    if request.method == "POST":
        form = InstructorProfilePictureForm(
            request.POST,
            request.FILES,
            instance=instructor
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("instructor_profile")

    else:
        form = InstructorProfilePictureForm(instance=instructor)

    return render(request, "profile_picture_upload.html", {"form": form, "picture": instructor.profile_picture})

#EXPORT INDIVIDUAL STUDENT's ATTENDANCE as PDF
def student_attendance_pdf(request, id):
    if not request.user.is_authenticated:
        return redirect("login")

    student = get_object_or_404(Student, id=id)

    if hasattr(request.user, "student"):
        if request.user.student.id != student.id:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
    elif not (request.user.is_staff or hasattr(request.user, "instructor")):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    attendances = Attendance.objects.filter(
        student=student
    ).order_by("date")

    present = attendances.filter(status="Present").count()
    absent = attendances.filter(status="Absent").count()
    total = attendances.count()

    percentage = 0
    if total > 0:
        percentage = round((present / total) * 100, 2)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{student.full_name}_attendance_report.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal = styles["Normal"]

    elements = []

    # Header

    elements.append(
        Paragraph("<b>EDUTRACK</b>", title_style)
    )

    elements.append(
        Paragraph(
            "Student Management System",
            heading_style,
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "<b>STUDENT ATTENDANCE REPORT</b>",
            heading_style,
        )
    )

    elements.append(Spacer(1, 25))

    # Student Information

    info = [
        ["Student Name", student.full_name],
        ["Enrollment Number", student.enrollment_number],
        ["Course", student.enrolled_course.course_name],
        ["Generated On", date.today().strftime("%d %B %Y")],
    ]

    info_table = Table(info, colWidths=[170, 300])

    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(info_table)

    elements.append(Spacer(1, 25))

    # Attendance Records

    elements.append(
        Paragraph("<b>Attendance Records</b>", styles["Heading3"])
    )

    elements.append(Spacer(1, 10))

    data = [
        ["Date", "Status"]
    ]

    for attendance in attendances:
        data.append([
            attendance.date.strftime("%d %b %Y"),
            attendance.status,
        ])

    attendance_table = Table(
        data,
        colWidths=[250, 200],
    )

    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ])

    # Alternate row colors
    for row in range(1, len(data)):
        bg = colors.whitesmoke if row % 2 == 0 else colors.beige
        table_style.add(
            "BACKGROUND",
            (0, row),
            (-1, row),
            bg,
        )

    attendance_table.setStyle(table_style)

    elements.append(attendance_table)

    elements.append(Spacer(1, 25))

    # Summary

    elements.append(
        Paragraph("<b>Attendance Summary</b>", styles["Heading3"])
    )

    elements.append(Spacer(1, 10))

    summary = [
        ["Present Records", str(present)],
        ["Absent Records", str(absent)],
        ["Total Records", str(total)],
        ["Attendance Percentage", f"{percentage}%"],
    ]

    summary_table = Table(summary, colWidths=[220, 120])

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 30))

    # Footer

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by EduTrack</font>",
            normal,
        )
    )

    doc.build(elements)

    return response

#EXPORT INDIVIDUAL STUDENT's RESULT as PDF
def student_result_pdf(request, id):
    if not request.user.is_authenticated:
        return redirect("login")

    student = get_object_or_404(Student, id=id)

    if hasattr(request.user, "student"):
        if request.user.student.id != student.id:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
    elif not (request.user.is_staff or hasattr(request.user, "instructor")):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    results = Result.objects.filter(
        student=student
    ).select_related("module").order_by("module__module_name")

    total_modules = results.count()

    total_full_marks = 0
    total_obtained = 0

    data = [["Module", "Full Marks", "Obtained Marks", "Percentage", "Grade"]]

    for result in results:

        full_marks = float(result.module.full_marks)
        obtained = float(result.obtained_marks)
        percentage_for_result = result_percentage(result)

        total_full_marks += full_marks
        total_obtained += obtained

        data.append([
            result.module.module_name,
            f"{full_marks:.0f}",
            f"{obtained:.0f}",
            f"{percentage_for_result:.2f}%",
            grade_for_percentage(percentage_for_result),
        ])

    percentage = 0

    if total_full_marks > 0:
        percentage = round(
            (total_obtained / total_full_marks) * 100,
            2
        )
    overall_grade = grade_for_percentage(percentage)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{student.full_name}_result_report.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal = styles["Normal"]

    elements = []

    # Header
    
    elements.append(
        Paragraph("<b>EDUTRACK</b>", title_style)
    )

    elements.append(
        Paragraph(
            "Student Management System",
            heading_style,
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "<b>STUDENT RESULT REPORT</b>",
            heading_style,
        )
    )

    elements.append(Spacer(1, 25))

    # Student Information

    info = [
        ["Student Name", student.full_name],
        ["Enrollment Number", student.enrollment_number],
        ["Course", student.enrolled_course.course_name],
        ["Generated On", date.today().strftime("%d %B %Y")],
    ]

    info_table = Table(info, colWidths=[170, 300])

    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(info_table)

    elements.append(Spacer(1, 25))

    # Results Table

    elements.append(
        Paragraph("<b>Academic Results</b>", styles["Heading3"])
    )

    elements.append(Spacer(1, 10))

    result_table = Table(
        data,
        colWidths=[150, 80, 100, 90, 60],
    )

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#198754")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ])

    for row in range(1, len(data)):
        background = (
            colors.whitesmoke
            if row % 2 == 0
            else colors.beige
        )

        style.add(
            "BACKGROUND",
            (0, row),
            (-1, row),
            background,
        )

    result_table.setStyle(style)

    elements.append(result_table)

    elements.append(Spacer(1, 25))

    # Summary

    elements.append(
        Paragraph("<b>Result Summary</b>", styles["Heading3"])
    )

    elements.append(Spacer(1, 10))

    summary = [
        ["Total Modules", str(total_modules)],
        ["Total Full Marks", f"{total_full_marks:.0f}"],
        ["Obtained Marks", f"{total_obtained:.0f}"],
        ["Percentage", f"{percentage}%"],
        ["Overall Grade", overall_grade],
    ]

    summary_table = Table(
        summary,
        colWidths=[220, 120],
    )

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by EduTrack</font>",
            normal,
        )
    )

    doc.build(elements)

    return response