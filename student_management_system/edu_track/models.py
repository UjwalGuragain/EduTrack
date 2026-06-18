from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    course_name  = models.CharField(max_length=100)
    DURATION_CHOICES = [
        (1, "1 Year"),
        (2, "2 Years"),
        (3, "3 Years"),
        (4, "4 Years"),
        (5, "5 years")
    ]
    course_duration = models.IntegerField(choices = DURATION_CHOICES)

    def __str__(self):
        return self.course_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True, blank = True)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=10)
    email = models.EmailField()
    guardian_name = models.CharField(max_length=100)
    enrollment_number = models.CharField(max_length=20, unique=True)
    enrolled_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField()

    def __str__(self):
        return self.full_name
    
class Module(models.Model):
    module_name = models.CharField(max_length=100)
    module_code = models.CharField(max_length=10)
    full_marks = models.DecimalField(max_digits=5, decimal_places=2)
    courses = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.module_name

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.module}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent")
    ]
    status = models.CharField(max_length=10, choices = STATUS_CHOICES)

    def __str__(self):
        return f"{self.student} - {self.date}"

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name