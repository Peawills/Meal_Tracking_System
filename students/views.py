from django.utils import timezone
from django.shortcuts import render,redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required , user_passes_test
import json
from .models import Student, FeedingRecord
from .forms import StudentForm



def is_admin(user):
    return user.is_superuser  # or user.is_staff if you want staff access too

@user_passes_test(is_admin)
def admin_dashboard(request):
    
    today = timezone.now().date()
    total_students = Student.objects.count()
    total_records_today = FeedingRecord.objects.filter(date=today).count()

    meals_today = FeedingRecord.objects.filter(date=today).values('meal_type').distinct()
    meal_counts = {
        meal['meal_type']: FeedingRecord.objects.filter(meal_type=meal['meal_type'], date=today).count()
        for meal in meals_today
    }

    return render(request, 'students/admin_dashboard.html', {
        'total_students': total_students,
        'total_records_today': total_records_today,
        'meal_counts': meal_counts,
        'today': today
    })


@user_passes_test(lambda u: u.is_superuser)
def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('register_student')  # or redirect to success page
    else:
        form = StudentForm()

    return render(request, 'students/register_student.html', {'form': form})

# ✅ GET student info from QR
@login_required
def scan_page(request):
    return render(request, 'students/scan_qr.html')

# ✅ Print all QR cards
@user_passes_test(lambda u: u.is_superuser)
@login_required
def print_qr_cards(request):
    query = request.GET.get('q', '').strip()
    student_id = request.GET.get('student_id')

    # Fetch all students only once
    all_students = Student.objects.all().order_by('name')
    students = Student.objects.all().order_by('class_name', 'name')

    if student_id:
        students = students.filter(id=student_id)
    elif query:
        students = students.filter(name__icontains=query)

    return render(request, 'students/print_qr_cards.html', {
        'students': students,
        'all_students': all_students
    })

# ✅ Feeding Records View with Class Filter
@user_passes_test(lambda u: u.is_superuser)
@login_required
def feeding_records(request):
    class_filter = request.GET.get('class')
    search_query = request.GET.get('search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    export = request.GET.get('export')

    records = FeedingRecord.objects.select_related('student')

    if class_filter:
        records = records.filter(student__class_name=class_filter)

    if search_query:
        records = records.filter(student__name__icontains=search_query)

    if start_date and end_date:
        records = records.filter(date__range=[start_date, end_date])

    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="meal_records.csv"'

        writer = csv.writer(response)
        writer.writerow(['Student', 'Class', 'Meal', 'Date', 'Time'])

        for record in records:
            writer.writerow([
                record.student.name,
                record.student.class_name,
                record.meal_type,
                record.date,
                record.timestamp.strftime('%H:%M:%S'),
            ])
        return response

    classes = Student.objects.values_list('class_name', flat=True).distinct()

    return render(request, 'students/feeding_records.html', {
        'records': records,
        'classes': classes,
        'selected_class': class_filter,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
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
