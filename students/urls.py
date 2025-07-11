from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #  Use this to make login the first/default page
    path('', auth_views.LoginView.as_view(template_name='students/login.html'), name='login'),

    path('print-qr-cards/', views.print_qr_cards, name='print_qr_cards'),
    path('scan/', views.scan_page, name='scan_qr'),
    path('api/student/<str:qr_code>/', views.get_student_by_qr, name='get_student_by_qr'),
    path('api/mark-fed/<str:qr_code>/', views.mark_student_as_fed, name='mark_student_as_fed'),
    path('records/', views.feeding_records, name='feeding_records'),
    path('register-student/', views.register_student, name='register_student'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ✅ Keep logout path
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
