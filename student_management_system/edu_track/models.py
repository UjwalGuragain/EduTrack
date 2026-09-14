from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Course(models.Model):
    course_name  = models.CharField(max_length=100)
    course_code = models.CharField(max_length=10)
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
    profile_picture = models.ImageField(upload_to="students/", blank=True, null=True)

    def __str__(self):
        return self.full_name
    
class AcademicYear(models.Model):
    """Academic year (e.g. 2025/2026) that semesters belong to."""
    year_label = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.year_label


class Semester(models.Model):
    """A semester belongs to one course within one academic year."""
    YEAR_LEVEL_CHOICES = [
        (1, "Year 1"),
        (2, "Year 2"),
        (3, "Year 3"),
        (4, "Year 4"),
        (5, "Year 5"),
    ]
    SEMESTER_NUMBER_CHOICES = [
        (1, "Semester 1"),
        (2, "Semester 2"),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="semesters")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="semesters")
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES, default=1)
    semester_number = models.IntegerField(choices=SEMESTER_NUMBER_CHOICES, default=1)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["course", "year_level", "semester_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "course", "year_level", "semester_number"],
                name="unique_semester_per_year_course"
            )
        ]

    def clean(self):
        if self.course_id and self.year_level > self.course.course_duration:
            raise ValidationError({
                "year_level": (
                    f"{self.course} is a {self.course.get_course_duration_display()} "
                    f"course, so it cannot have Year {self.year_level}."
                )
            })

    def __str__(self):
        return f"{self.course} - {self.academic_year} - {self.name}"


class Module(models.Model):
    module_name = models.CharField(max_length=100)
    module_code = models.CharField(max_length=10)
    full_marks = models.DecimalField(max_digits=5, decimal_places=2)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="modules")

    def __str__(self):
        return self.module_name

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "module"],
                name="unique_student_module_result"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.module}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
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
    profile_picture = models.ImageField(upload_to="instructors/", blank=True, null=True)

    def __str__(self):
        return self.full_name