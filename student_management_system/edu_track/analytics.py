"""Analytics helper functions for EduTrack dashboards.

Pure functions that compute Chart.js-friendly data structures
(labels + datasets) from the ORM. Kept separate from views so the
computation logic is easy to unit-test and reuse.
"""

from datetime import date, timedelta
from collections import Counter

from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone

from .models import Attendance, Result, Student

# Grade buckets in the same order as grade_for_percentage thresholds.
GRADE_ORDER = ["A+", "A", "B+", "B", "C", "D", "F"]


def result_percentage_for(result):
    """Percentage a single result represents of its module's full marks."""
    full_marks = float(result.module.full_marks)
    if full_marks <= 0:
        return 0
    return round((float(result.obtained_marks) / full_marks) * 100, 2)


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


def grade_distribution(queryset=None):
    """Distribution of letter grades across a set of results.

    Accepts an optional Result queryset (e.g. scoped to a student) and
    falls back to all results. Returns {'labels': [...], 'data': [...]}.
    """
    results = (
        Result.objects.select_related("module").all()
        if queryset is None
        else queryset
    )
    counts = {grade: 0 for grade in GRADE_ORDER}

    for result in results:
        percentage = result_percentage_for(result)
        grade = grade_for_percentage(percentage)
        counts[grade] += 1

    labels = [grade for grade in GRADE_ORDER if counts[grade] > 0]
    data = [counts[grade] for grade in GRADE_ORDER if counts[grade] > 0]
    return {"labels": labels, "data": data}


def attendance_trend(days=30, queryset=None):
    """Attendance present-count per day for the last N days.

    Days with no records are included with a 0 count so line charts
    show a continuous date axis.
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    attendance = Attendance.objects.all() if queryset is None else queryset
    dates = attendance.filter(
        date__gte=start_date,
        date__lte=end_date,
        status="Present",
    ).values_list("date", flat=True)
    count_map = Counter(dates)

    labels = []
    data = []
    current = start_date
    while current <= end_date:
        labels.append(current.strftime("%d %b"))
        data.append(count_map.get(current, 0))
        current += timedelta(days=1)

    return {"labels": labels, "data": data}


def course_average_scores():
    """Average percentage score per course (from Result + full marks).

    Returns {'labels': [course names], 'data': [avg percentage]}.
    """
    results = (
        Result.objects.select_related("module__semester__course")
        .values("module__semester__course__course_name")
        .annotate(
            total_obtained=Sum("obtained_marks"),
            total_full=Sum("module__full_marks"),
            result_count=Count("id"),
        )
        .order_by("module__semester__course__course_name")
    )

    labels = []
    data = []
    for item in results:
        full = float(item["total_full"] or 0)
        if full <= 0:
            continue
        labels.append(item["module__semester__course__course_name"])
        percentage = round((float(item["total_obtained"]) / full) * 100, 2)
        data.append(percentage)
    return {"labels": labels, "data": data}


def enrollment_by_month():
    """Number of student enrollments grouped by month (last 12 months).

    Returns {'labels': ['Jan 2026', ...], 'data': [...]}.
    """
    enrollment_dates = Student.objects.values_list("enrollment_date", flat=True)
    month_counts = Counter(
        (enrollment_date.year, enrollment_date.month)
        for enrollment_date in enrollment_dates
        if enrollment_date
    )
    labels = [
        date(year, month, 1).strftime("%b %Y")
        for year, month in sorted(month_counts)
    ]
    data = [month_counts[month] for month in sorted(month_counts)]
    return {"labels": labels, "data": data}


def course_enrollment_counts():
    """Number of students enrolled in each course."""
    students = (
        Student.objects.select_related("enrolled_course")
        .values("enrolled_course__course_name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    labels = [item["enrolled_course__course_name"] for item in students]
    data = [item["count"] for item in students]
    return {"labels": labels, "data": data}


def module_average_scores():
    """Average percentage score per module.

    Returns {'labels': [module names], 'data': [avg percentage]}.
    """
    results = (
        Result.objects.select_related("module")
        .values("module__module_name")
        .annotate(
            total_obtained=Sum("obtained_marks"),
            total_full=Sum("module__full_marks"),
        )
        .order_by("module__module_name")
    )
    labels = []
    data = []
    for item in results:
        full = float(item["total_full"] or 0)
        if full <= 0:
            continue
        labels.append(item["module__module_name"])
        percentage = round((float(item["total_obtained"]) / full) * 100, 2)
        data.append(percentage)
    return {"labels": labels, "data": data}


def student_module_performance(student):
    """A student's obtained vs full marks per module (grouped bar chart)."""
    results = (
        Result.objects.filter(student=student)
        .select_related("module")
        .order_by("module__module_name")
    )
    labels = [result.module.module_name for result in results]
    obtained = [float(result.obtained_marks) for result in results]
    full_marks = [float(result.module.full_marks) for result in results]
    return {
        "labels": labels,
        "obtained": obtained,
        "full_marks": full_marks,
    }


def student_grade_history(student):
    """A student's percentage and letter grade per module."""
    results = (
        Result.objects.filter(student=student)
        .select_related("module")
        .order_by("module__module_name")
    )
    labels = [result.module.module_name for result in results]
    percentages = [result_percentage_for(result) for result in results]
    grades = [grade_for_percentage(percentage) for percentage in percentages]
    return {
        "labels": labels,
        "percentages": percentages,
        "grades": grades,
    }


def top_performing_students(limit=5):
    """Top N students by overall percentage (those with results only)."""
    aggregates = (
        Result.objects.select_related("student")
        .values("student__full_name", "student__enrollment_number")
        .annotate(
            total_obtained=Sum("obtained_marks"),
            total_full=Sum("module__full_marks"),
        )
        .order_by("-total_obtained")
    )
    rows = []
    for item in aggregates:
        full = float(item["total_full"] or 0)
        if full <= 0:
            continue
        percentage = round((float(item["total_obtained"]) / full) * 100, 2)
        rows.append(
            {
                "name": item["student__full_name"],
                "enrollment_number": item["student__enrollment_number"],
                "percentage": percentage,
                "grade": grade_for_percentage(percentage),
            }
        )
    rows.sort(key=lambda row: row["percentage"], reverse=True)
    return rows[:limit]


def bottom_performing_students(limit=5):
    """Bottom N students by overall percentage (those with results only)."""
    rows = top_performing_students(limit=None)
    return sorted(rows, key=lambda row: row["percentage"])[:limit]


def attendance_percentage_for(attendance_queryset):
    """Present percentage for a given queryset of attendance records."""
    total = attendance_queryset.count()
    if total == 0:
        return 0
    present = attendance_queryset.filter(status="Present").count()
    return round((present / total) * 100, 2)


def summary_stats(queryset=None):
    """A handful of high-level aggregations for the analytics header cards."""
    results = Result.objects.all() if queryset is None else queryset
    stats = results.aggregate(
        total=Count("id"),
        average=Avg("obtained_marks"),
        highest=Max("obtained_marks"),
        lowest=Min("obtained_marks"),
    )
    return {
        "total_results": stats["total"] or 0,
        "average_marks": round(float(stats["average"] or 0), 2),
        "highest_marks": float(stats["highest"] or 0),
        "lowest_marks": float(stats["lowest"] or 0),
    }