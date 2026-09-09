from django.test import TestCase, Client
from django.contrib.auth.models import User
from edu_track.models import Instructor, Student, Course, Module, Result, Attendance
from edu_track.serializers import StudentSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

#Test-1 covering critical bug fixes

class CriticalBugFixTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="instructor1", password="password123")
        self.instructor = Instructor.objects.create(
            user=self.user,
            full_name="Prof Test",
            contact_number="1234567890",
            email="prof@test.com",
            address="Kathmandu",
            qualification="PhD"
        )
        self.client.force_login(self.user)

        self.course = Course.objects.create(
            course_name="Computer Science",
            course_code="CS101",
            course_duration=4
        )
        self.module = Module.objects.create(
            module_name="Algorithms",
            module_code="CS102",
            full_marks=100,
            courses=self.course
        )
        self.student1 = Student.objects.create(
            full_name="Alice Smith",
            address="Kathmandu",
            contact_number="9800000001",
            email="alice@test.com",
            guardian_name="Bob",
            enrollment_number="EN001",
            enrolled_course=self.course,
            enrollment_date="2026-01-01"
        )
        self.student2 = Student.objects.create(
            full_name="Charlie Brown",
            address="Pokhara",
            contact_number="9800000002",
            email="charlie@test.com",
            guardian_name="David",
            enrollment_number="EN002",
            enrolled_course=self.course,
            enrollment_date="2026-01-01"
        )
        self.result1 = Result.objects.create(
            student=self.student1,
            module=self.module,
            obtained_marks=85
        )
        self.attendance1 = Attendance.objects.create(
            student=self.student1,
            date="2026-03-01",
            status="Present"
        )

    def test_student_search_and_pagination(self):
        response = self.client.get("/student/?search=Alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["students"]), 1)
        self.assertEqual(response.context["students"][0].full_name, "Alice Smith")

    def test_result_search_and_pagination(self):
        response = self.client.get("/result/?search=Alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0].student.full_name, "Alice Smith")

    def test_attendance_search_and_pagination(self):
        response = self.client.get("/attendance/?search=Alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["attendance"]), 1)
        self.assertEqual(response.context["attendance"][0].student.full_name, "Alice Smith")

    def test_serializer_create_and_update(self):
        data = {
            "full_name": "Serializer Student",
            "address": "Lalitpur",
            "contact_number": "9800000005",
            "email": "ser@test.com",
            "guardian_name": "Guard",
            "enrollment_number": "EN005",
            "enrollment_date": "2026-01-01",
            "enrolled_course": {
                "course_name": "Data Science",
                "course_code": "DS101",
                "course_duration": 3
            }
        }
        serializer = StudentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        student_obj = serializer.save()
        self.assertEqual(student_obj.enrolled_course.course_name, "Data Science")

        update_data = {
            "full_name": "Updated Serializer Student",
            "enrolled_course": {
                "course_name": "Data Science",
                "course_code": "DS101",
                "course_duration": 3
            }
        }
        update_serializer = StudentSerializer(instance=student_obj, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_obj = update_serializer.save()
        self.assertEqual(updated_obj.full_name, "Updated Serializer Student")

    def test_student_add_with_empty_user(self):
        response = self.client.post("/student/add/", {
            "user": "",
            "full_name": "Empty User Student",
            "address": "Bhaktapur",
            "contact_number": "9800000006",
            "email": "emptyuser@test.com",
            "guardian_name": "Parent",
            "enrollment_number": "EN006",
            "enrolled_course": str(self.course.id),
            "enrollment_date": "2026-01-01"
        })
        self.assertEqual(response.status_code, 302)
        student = Student.objects.get(enrollment_number="EN006")
        self.assertIsNone(student.user)

    def test_student_update_user_dropdown_and_save(self):
        student_user = User.objects.create_user(username="student_user", password="password123")
        self.student1.user = student_user
        self.student1.save()

        get_response = self.client.get(f"/student/update/{self.student1.id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertIn(student_user, get_response.context["users"])

        post_response = self.client.post(f"/student/update/{self.student1.id}/", {
            "user": str(student_user.id),
            "full_name": "Alice Smith Updated",
            "address": "Kathmandu",
            "contact_number": "9800000001",
            "email": "alice@test.com",
            "guardian_name": "Bob",
            "enrollment_number": "EN001",
            "enrolled_course": str(self.course.id),
            "enrollment_date": "2026-01-01"
        })
        self.assertEqual(post_response.status_code, 302)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.user, student_user)
        self.assertEqual(self.student1.full_name, "Alice Smith Updated")

    def test_student_import_csv_error_handling(self):
        csv_content = (
            "Full Name,Address,Contact Number,Email,Guardian Name,Enrollment Number,Enrolled Course,Enrollment Date\n"
            "Bad Course Student,Test,1234567890,b@test.com,Guard,EN999,Nonexistent Course,2026-01-01\n"
            "Dup Student,Test,1234567890,dup@test.com,Guard,EN001,Computer Science,2026-01-01\n"
            "Good Student,Test,1234567890,good@test.com,Guard,EN100,Computer Science,2026-01-01\n"
        )
        uploaded = SimpleUploadedFile("students.csv", csv_content.encode("utf-8"), content_type="text/csv")
        response = self.client.post("/student/import/csv/", {"csv_file": uploaded}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(enrollment_number="EN100").exists())
        self.assertFalse(Student.objects.filter(enrollment_number="EN999").exists())

#Test-2 covering business logic and dashboard flows
class BusinessLogicAndDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Instructor setup
        self.instructor_user = User.objects.create_user(username="prof_john", password="Password123")
        self.instructor = Instructor.objects.create(
            user=self.instructor_user,
            full_name="Prof John",
            contact_number="9841234567",
            email="john@test.com",
            address="Kathmandu",
            qualification="MSc CS"
        )

        # Student 1 setup
        self.student_user1 = User.objects.create_user(username="student_alice", password="Password123")
        self.course1 = Course.objects.create(
            course_name="Software Engineering",
            course_code="SE101",
            course_duration=4
        )
        self.course_empty = Course.objects.create(
            course_name="Empty Course Without Modules",
            course_code="EC101",
            course_duration=2
        )
        self.module1 = Module.objects.create(
            module_name="Web Architecture",
            module_code="SE201",
            full_marks=100,
            courses=self.course1
        )
        self.module2 = Module.objects.create(
            module_name="Database Systems",
            module_code="SE202",
            full_marks=100,
            courses=self.course1
        )
        self.student1 = Student.objects.create(
            user=self.student_user1,
            full_name="Alice Wonderland",
            address="Lalitpur",
            contact_number="9811111111",
            email="alice.w@test.com",
            guardian_name="Queen",
            enrollment_number="SE001",
            enrolled_course=self.course1,
            enrollment_date="2026-01-15"
        )

        # Student 2 setup (without attendance or results)
        self.student_user2 = User.objects.create_user(username="student_bob", password="Password123")
        self.student2 = Student.objects.create(
            user=self.student_user2,
            full_name="Bob Builder",
            address="Patan",
            contact_number="9822222222",
            email="bob.b@test.com",
            guardian_name="Wendy",
            enrollment_number="SE002",
            enrolled_course=self.course1,
            enrollment_date="2026-02-01"
        )

        # Add attendance and result for student 1 only
        self.att1 = Attendance.objects.create(student=self.student1, date="2026-03-01", status="Present")
        self.res1 = Result.objects.create(student=self.student1, module=self.module1, obtained_marks=92)

    def test_instructor_dashboard_metrics(self):
        self.client.force_login(self.instructor_user)
        response = self.client.get("/instructor/dashboard/")
        self.assertEqual(response.status_code, 200)

        # 1 course has modules (course1), 1 course has no modules (course_empty)
        self.assertEqual(response.context["courses_without_modules"], 1)

        # student2 has no attendance, student1 has attendance
        self.assertEqual(response.context["students_without_attendance"], 1)

        # student2 has no results, student1 has results
        self.assertEqual(response.context["students_without_results"], 1)

        # Counts
        self.assertEqual(response.context["student_count"], 2)
        self.assertEqual(response.context["course_count"], 2)
        self.assertEqual(response.context["module_count"], 2)
        self.assertEqual(response.context["result_count"], 1)

    def test_student_module_view_shows_course_modules(self):
        # Student 2 has no results yet, but should still see all modules of their enrolled course
        self.client.force_login(self.student_user2)
        response = self.client.get("/student/my-module/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["modules"]), 2)
        module_codes = [m.module_code for m in response.context["modules"]]
        self.assertIn("SE201", module_codes)
        self.assertIn("SE202", module_codes)

    def test_student_dashboard_and_views(self):
        self.client.force_login(self.student_user1)

        # Dashboard
        resp_dash = self.client.get("/student/dashboard/")
        self.assertEqual(resp_dash.status_code, 200)
        self.assertEqual(resp_dash.context["present_count"], 1)
        self.assertEqual(resp_dash.context["absent_count"], 0)
        self.assertEqual(resp_dash.context["result_count"], 1)

        # Course
        resp_course = self.client.get("/student/my-course/")
        self.assertEqual(resp_course.status_code, 200)

        # Attendance
        resp_att = self.client.get("/student/my-attendance/")
        self.assertEqual(resp_att.status_code, 200)

        # Results
        resp_res = self.client.get("/student/my-result/")
        self.assertEqual(resp_res.status_code, 200)
        self.assertEqual(resp_res.context["highest_marks"], 92.0)

    def test_pdf_access_control(self):
        # 1. Unauthenticated user gets redirected to login
        unauth_client = Client()
        resp_unauth = unauth_client.get(f"/student/{self.student1.id}/attendance-report/")
        self.assertEqual(resp_unauth.status_code, 302)
        self.assertIn("/login", resp_unauth.url)

        # 2. Instructor can download student report
        self.client.force_login(self.instructor_user)
        resp_inst_att = self.client.get(f"/student/{self.student1.id}/attendance-report/")
        self.assertEqual(resp_inst_att.status_code, 200)
        self.assertEqual(resp_inst_att["Content-Type"], "application/pdf")

        resp_inst_res = self.client.get(f"/student/{self.student1.id}/result-report/")
        self.assertEqual(resp_inst_res.status_code, 200)
        self.assertEqual(resp_inst_res["Content-Type"], "application/pdf")

        # 3. Student can download their own report
        self.client.force_login(self.student_user1)
        resp_stud_own = self.client.get(f"/student/{self.student1.id}/attendance-report/")
        self.assertEqual(resp_stud_own.status_code, 200)
        self.assertEqual(resp_stud_own["Content-Type"], "application/pdf")

        # 4. Student CANNOT download another student's report (403 PermissionDenied)
        resp_stud_other = self.client.get(f"/student/{self.student2.id}/attendance-report/")
        self.assertEqual(resp_stud_other.status_code, 403)

    def test_user_registration_password_length(self):
        # 8 characters should succeed
        resp = self.client.post("/register/", {
            "username": "new_user_8char",
            "email": "new8@test.com",
            "password1": "12345678",
            "password2": "12345678",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="new_user_8char").exists())


#Test-3 covering API permission architecture
class APIPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_user(
            username="admin_user", password="adminpass123", is_staff=True
        )

        # Instructor
        self.instructor_user = User.objects.create_user(
            username="prof_api", password="instructpass123"
        )
        self.instructor = Instructor.objects.create(
            user=self.instructor_user,
            full_name="Prof API",
            contact_number="9841234567",
            email="profapi@test.com",
            address="Kathmandu",
            qualification="PhD"
        )

        # Course + module
        self.course = Course.objects.create(
            course_name="Computer Science", course_code="CS101", course_duration=4
        )
        self.module = Module.objects.create(
            module_name="Algorithms", module_code="CS201", full_marks=100,
            courses=self.course
        )

        # Two students
        self.student_user1 = User.objects.create_user(
            username="student_api1", password="studentpass123"
        )
        self.student1 = Student.objects.create(
            user=self.student_user1,
            full_name="API Alice",
            address="Kathmandu",
            contact_number="9811111111",
            email="apialice@test.com",
            guardian_name="Guard A",
            enrollment_number="API001",
            enrolled_course=self.course,
            enrollment_date="2026-01-01"
        )
        self.student_user2 = User.objects.create_user(
            username="student_api2", password="studentpass123"
        )
        self.student2 = Student.objects.create(
            user=self.student_user2,
            full_name="API Bob",
            address="Patan",
            contact_number="9822222222",
            email="apibob@test.com",
            guardian_name="Guard B",
            enrollment_number="API002",
            enrolled_course=self.course,
            enrollment_date="2026-01-01"
        )

        self.result1 = Result.objects.create(
            student=self.student1, module=self.module, obtained_marks=88
        )
        self.att1 = Attendance.objects.create(
            student=self.student1, date="2026-03-01", status="Present"
        )

    # --- Unauthenticated (denied) ---
    def test_unauthenticated_denied_all_endpoints(self):
        # Force logout by using a fresh client with no session
        unauth = Client()
        for url in [
            "/api/v1/students/",
            "/api/v1/instructors/",
            "/api/v1/courses/",
            "/api/v1/modules/",
            "/api/v1/attendances/",
            "/api/v1/results/",
        ]:
            resp = unauth.get(url)
            self.assertIn(
                resp.status_code, (401, 403),
                f"Expected 401/403 for GET {url}, got {resp.status_code}",
            )

    # --- Students list access ---
    def test_student_can_list_only_own_record(self):
        self.client.force_login(self.student_user1)
        resp = self.client.get("/api/v1/students/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["enrollment_number"], "API001")

    def test_student_cannot_view_another_students_object(self):
        self.client.force_login(self.student_user1)
        resp = self.client.get(f"/api/v1/students/{self.student2.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_instructor_can_list_all_students(self):
        self.client.force_login(self.instructor_user)
        resp = self.client.get("/api/v1/students/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_student_cannot_create_or_update_students(self):
        self.client.force_login(self.student_user1)
        # Create -> forbidden
        resp = self.client.post("/api/v1/students/", {
            "full_name": "Hacker",
            "address": "X",
            "contact_number": "9800000000",
            "email": "hack@test.com",
            "guardian_name": "G",
            "enrollment_number": "HACK001",
            "enrolled_course": self.course.id,
            "enrollment_date": "2026-01-01",
        })
        self.assertEqual(resp.status_code, 403)

        # Update another student -> forbidden
        resp = self.client.patch(
            f"/api/v1/students/{self.student2.id}/",
            {"full_name": "Hacked"},
        )
        self.assertEqual(resp.status_code, 403)

    # --- Instructors endpoint ---
    def test_student_cannot_access_instructors(self):
        self.client.force_login(self.student_user1)
        resp = self.client.get("/api/v1/instructors/")
        self.assertEqual(resp.status_code, 403)

    def test_instructor_read_only_on_instructors_endpoint(self):
        self.client.force_login(self.instructor_user)
        # Can list
        resp = self.client.get("/api/v1/instructors/")
        self.assertEqual(resp.status_code, 200)
        # Cannot create (POST on instructors allowed for admins only)
        resp = self.client.post("/api/v1/instructors/", {
            "user": self.instructor_user.id,
            "full_name": "New Prof",
            "contact_number": "1234567890",
            "email": "newprof@test.com",
            "address": "X",
            "qualification": "MSc",
        })
        self.assertEqual(resp.status_code, 403)

    def test_admin_full_access_to_instructors(self):
        self.client.force_login(self.admin_user)
        new_admin = User.objects.create_user(
            username="admin_prof", password="adminpass123"
        )
        resp = self.client.post("/api/v1/instructors/", {
            "user": new_admin.id,
            "full_name": "Admin Prof",
            "contact_number": "1234567890",
            "email": "adminprof@test.com",
            "address": "X",
            "qualification": "PhD",
        })
        self.assertEqual(resp.status_code, 201)

    # --- Courses & Modules: instructor write, student read-only ---
    def test_student_read_only_on_courses_and_modules(self):
        self.client.force_login(self.student_user1)
        resp_get = self.client.get("/api/v1/courses/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post("/api/v1/courses/", {
            "course_name": "Hacked Course",
            "course_code": "HACK",
            "course_duration": 2,
        })
        self.assertEqual(resp_post.status_code, 403)

    def test_instructor_can_write_courses(self):
        self.client.force_login(self.instructor_user)
        resp = self.client.post("/api/v1/courses/", {
            "course_name": "AI",
            "course_code": "AI101",
            "course_duration": 3,
        })
        self.assertEqual(resp.status_code, 201)

    # --- Attendance & Results object-level ownership ---
    def test_student_can_only_read_own_attendance(self):
        self.client.force_login(self.student_user1)
        # Own attendance visible in list
        resp = self.client.get("/api/v1/attendances/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

        # Cannot see another student's attendance object
        self.student2_att = Attendance.objects.create(
            student=self.student2, date="2026-03-02", status="Absent"
        )
        resp = self.client.get(f"/api/v1/attendances/{self.student2_att.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_student_cannot_write_attendance_or_results(self):
        self.client.force_login(self.student_user1)
        resp_att = self.client.post("/api/v1/attendances/", {
            "student": self.student2.id,
            "date": "2026-03-05",
            "status": "Present",
        })
        self.assertEqual(resp_att.status_code, 403)

        resp_res = self.client.post("/api/v1/results/", {
            "student": self.student2.id,
            "module": self.module.id,
            "obtained_marks": 99,
        })
        self.assertEqual(resp_res.status_code, 403)

    def test_instructor_can_read_and_write_results(self):
        self.client.force_login(self.instructor_user)
        resp = self.client.post("/api/v1/results/", {
            "student": self.student2.id,
            "module": self.module.id,
            "obtained_marks": 75,
        })
        self.assertEqual(resp.status_code, 201)

    def test_student_can_only_read_own_results(self):
        self.client.force_login(self.student_user1)
        resp = self.client.get("/api/v1/results/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
