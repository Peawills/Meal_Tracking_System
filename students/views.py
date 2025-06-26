from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.contrib.admin.views.decorators import staff_member_required
from .models import Student, FeedingRecord

# ✅ GET student info from QR
@login_required
def scan_page(request):
    return render(request, 'students/scan_qr.html')

# ✅ Print all QR cards
@staff_member_required
@login_required
def print_qr_cards(request):
    students = Student.objects.all().order_by('class_name', 'name')
    return render(request, 'students/print_qr_cards.html', {'students': students})

# ✅ Feeding Records View with Class Filter
@login_required
def feeding_records(request):
    class_filter = request.GET.get('class')
    search_query = request.GET.get('search')

    records = FeedingRecord.objects.select_related('student')

    if class_filter:
        records = records.filter(student__class_name=class_filter)

    if search_query:
        records = records.filter(student__name__icontains=search_query)

    classes = Student.objects.values_list('class_name', flat=True).distinct()

    return render(request, 'students/feeding_records.html', {
        'records': records,
        'classes': classes,
        'selected_class': class_filter,
        'search_query': search_query,
    })

# ✅ API: Get Student by QR Code
@csrf_exempt
@login_required
def get_student_by_qr(request, qr_code):
    try:
        student = Student.objects.only('name', 'class_name', 'photo').get(qr_code_id=qr_code)
        data = {
            'name': student.name,
            'class_name': student.class_name,
            'photo_url': student.photo.url if student.photo else '',
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        raise Http404("Student not found")

# ✅ API: Mark Student as Fed
@csrf_exempt
@login_required
def mark_student_as_fed(request, qr_code):
    try:
        student = Student.objects.get(qr_code_id=qr_code)
        data = json.loads(request.body)
        meal_type = data.get('meal_type')
        today = timezone.now().date()

        if FeedingRecord.objects.filter(student=student, meal_type=meal_type, date=today).exists():
            return JsonResponse({'status': 'already_fed'})

        FeedingRecord.objects.create(
            student=student,
            class_name=student.class_name,
            meal_type=meal_type,
            date=today,
            time=timezone.now().time()
        )
        return JsonResponse({'status': 'success'})

    except Student.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
