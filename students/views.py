import csv
import json
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, FeedingRecord
from .forms import StudentForm
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.contrib import messages


# PDF tools
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def is_admin(user):
    return user.is_superuser  # or user.is_staff if you want staff too


@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)

    # Basic stats
    total_students = Student.objects.count()

    # Today's stats
    today_records = FeedingRecord.objects.filter(date=today)
    total_records_today = today_records.count()
    unique_students_today = today_records.values("student_id").distinct().count()

    # Meal counts for today
    breakfast_today = today_records.filter(meal_type="breakfast").count()
    lunch_today = today_records.filter(meal_type="lunch").count()
    dinner_today = today_records.filter(meal_type="dinner").count()
    snack_today = today_records.filter(meal_type="night_snack").count()

    # Weekly and monthly stats
    total_records_week = FeedingRecord.objects.filter(date__gte=week_ago).count()
    total_records_month = FeedingRecord.objects.filter(date__gte=month_start).count()

    # Meal breakdown
    meal_counts = {
        "breakfast": breakfast_today,
        "lunch": lunch_today,
        "dinner": dinner_today,
        "night_snack": snack_today,
    }

    # Remove meals with 0 count for cleaner display
    meal_counts = {k: v for k, v in meal_counts.items() if v > 0}

    # Recent activity (last 10 records)
    recent_records = (
        FeedingRecord.objects.select_related("student")
        .filter(date=today)
        .order_by("-time")[:10]
    )

    context = {
        "total_students": total_students,
        "total_records_today": total_records_today,
        "unique_students_today": unique_students_today,
        "breakfast_today": breakfast_today,
        "lunch_today": lunch_today,
        "dinner_today": dinner_today,
        "snack_today": snack_today,
        "total_records_week": total_records_week,
        "total_records_month": total_records_month,
        "meal_counts": meal_counts,
        "today": today,
        "recent_records": recent_records,
    }

    return render(request, "students/admin_dashboard.html", context)


@user_passes_test(is_admin)
def register_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("register_student")
    else:
        form = StudentForm()

    return render(request, "students/register_student.html", {"form": form})


@login_required
def scan_page(request):
    return render(request, "students/scan_qr.html")


@user_passes_test(is_admin)
@login_required
def print_qr_cards(request):
    query = request.GET.get("q", "")
    class_filter = request.GET.get("class", "")
    student_id = request.GET.get("student_id", "")

    students = Student.objects.all()

    # Apply filters
    if query:
        students = students.filter(name__icontains=query)

    if class_filter:
        students = students.filter(class_name=class_filter)

    if student_id:
        students = students.filter(id=student_id)

    # Get all students and classes for dropdowns
    all_students = Student.objects.all().order_by("name")
    classes = Student.objects.values_list("class_name", flat=True).distinct()
    total_students = Student.objects.count()

    context = {
        "students": students,
        "all_students": all_students,
        "classes": classes,
        "total_students": total_students,
    }

    return render(request, "students/print_qr_cards.html", context)


@user_passes_test(is_admin)
@login_required
def feeding_records(request):
    class_filter = request.GET.get("class")
    search_query = request.GET.get("search")
    meal_filter = request.GET.get("meal_type")
    selected_date = request.GET.get("date")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    export = request.GET.get("export")

    # Base queryset
    records = FeedingRecord.objects.select_related("student").order_by("-date", "-time")

    # Filter by class
    if class_filter:
        records = records.filter(student__class_name=class_filter)

    # Search by name or admission number
    if search_query:
        records = records.filter(
            Q(student__name__icontains=search_query)
            | Q(student__admission_number__icontains=search_query)
        )

    # Filter by meal type
    if meal_filter:
        records = records.filter(meal_type=meal_filter)

    # Date filtering with proper parsing
    use_date_range = False
    
    if start_date and end_date:
        # Parse dates properly
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        if start and end:
            records = records.filter(date__range=[start, end])
            use_date_range = True
        else:
            messages.error(request, "Invalid date format")
            
    elif start_date:
        start = parse_date(start_date)
        if start:
            records = records.filter(date__gte=start)
            use_date_range = True
        else:
            messages.error(request, "Invalid start date format")
            
    elif end_date:
        end = parse_date(end_date)
        if end:
            records = records.filter(date__lte=end)
            use_date_range = True
        else:
            messages.error(request, "Invalid end date format")
            
    elif selected_date:
        date_obj = parse_date(selected_date)
        if date_obj:
            records = records.filter(date=date_obj)
        else:
            messages.error(request, "Invalid date format")

    # CSV Export (rest remains the same)
    if export == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="meal_records.csv"'
        writer = csv.writer(response)
        writer.writerow(["Student", "Admission Number", "Class", "Meal", "Date", "Time"])
        
        for record in records:
            writer.writerow([
                record.student.name,
                record.student.admission_number,
                record.student.class_name,
                record.get_meal_type_display(),
                record.date.strftime("%Y-%m-%d"),
                record.time.strftime("%H:%M:%S"),
            ])
        return response

    # PDF Export (rest remains the same)
    if export == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="meal_records.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph("Meal Attendance Records", styles["Title"]))
        elements.append(Paragraph(datetime.now().strftime("%B %d, %Y %H:%M"), styles["Normal"]))
        elements.append(Paragraph(" ", styles["Normal"]))
        
        data = [["Student", "Admission Number", "Class", "Meal", "Date", "Time"]]
        for record in records:
            data.append([
                record.student.name,
                record.student.admission_number,
                record.student.class_name,
                record.get_meal_type_display(),
                record.date.strftime("%Y-%m-%d"),
                record.time.strftime("%H:%M:%S"),
            ])
        
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        doc.build(elements)
        return response

    # Stats
    show_stats = True
    total_records = records.count()
    unique_students = records.values("student_id").distinct().count()
    breakfast_count = records.filter(meal_type="breakfast").count()
    lunch_count = records.filter(meal_type="lunch").count()
    dinner_count = records.filter(meal_type="dinner").count()

    # Get distinct classes
    classes = Student.objects.values_list("class_name", flat=True).distinct().order_by("class_name")

    return render(request, "students/feeding_records.html", {
        "records": records,
        "classes": classes,
        "selected_class": class_filter,
        "selected_meal": meal_filter,
        "search_query": search_query,
        "selected_date": selected_date,
        "start_date": start_date,
        "end_date": end_date,
        "use_date_range": use_date_range,
        "show_stats": show_stats,
        "total_records": total_records,
        "unique_students": unique_students,
        "breakfast_count": breakfast_count,
        "lunch_count": lunch_count,
        "dinner_count": dinner_count,
    })
    
    
    
# ✅ API: Get Student by QR Code
@login_required
def get_student_by_qr(request, qr_code):
    try:
        student = Student.objects.only("name", "class_name", "photo").get(
            qr_code_id=qr_code
        )
        data = {
            "name": student.name,
            "class_name": student.class_name,
            "photo_url": student.photo.url if student.photo else "",
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        raise Http404("Student not found")


# ✅ API: Mark Student as Fed
@login_required
def mark_student_as_fed(request, qr_code):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )

    try:
        student = Student.objects.get(qr_code_id=qr_code)
        data = json.loads(request.body)
        meal_type = data.get("meal_type")
        today = timezone.now().date()

        if FeedingRecord.objects.filter(
            student=student, meal_type=meal_type, date=today
        ).exists():
            return JsonResponse({"status": "already_fed"})

        FeedingRecord.objects.create(
            student=student,
            class_name=student.class_name,
            meal_type=meal_type,
            date=today,
        )
        return JsonResponse({"status": "success"})

    except Student.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Student not found"}, status=404
        )


def export_feeding_records_csv(request):
    # ✅ Apply same filters as feeding record list
    records = FeedingRecord.objects.select_related("student").order_by("-date", "-time")

    selected_class = request.GET.get("class")
    search_query = request.GET.get("search")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if selected_class:
        records = records.filter(class_name=selected_class)

    if search_query:
        records = records.filter(
            Q(student__name__icontains=search_query)
            | Q(student__admission_number__icontains=search_query)
        )

    if start_date:
        records = records.filter(date__gte=start_date)

    if end_date:
        records = records.filter(date__lte=end_date)

    # ✅ CSV Response setup
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="feeding_records_{timezone.now().date()}.csv"'
    )

    writer = csv.writer(response)
    # ✅ CSV Header
    writer.writerow(
        ["Student Name", "Admission Number", "Class", "Meal", "Date", "Time"]
    )

    # ✅ Write rows
    for record in records:
        writer.writerow(
            [
                record.student.name,
                record.student.admission_number,
                record.class_name,
                record.get_meal_type_display(),
                record.date.strftime("%Y-%m-%d"),
                record.time.strftime("%H:%M:%S"),
            ]
        )

    return response