from django.db import models

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
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=10)
    email = models.EmailField()
    guardian_name = models.CharField(max_length=100)
    enrolled_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField()

    def __str__(self):
        return self.full_name
    
