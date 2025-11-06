# meal_tracker/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path(
        "", RedirectView.as_view(url="/accounts/login/", permanent=False)
    ),  # Redirect root to login when not authenticated
    path(
        "accounts/login/",
        LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("dashboard/", include("students.urls")),  # All student URLs including homepage
]
# ✅ This part serves media files (like photos or QR images) only in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
