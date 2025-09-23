from django.utils import timezone
from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.core.files import File


class Student(models.Model):
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    admission_number = models.CharField(max_length=30, unique=True, blank=False)
    qr_code_id = models.CharField(max_length=100, unique=True, blank=True)
    photo = models.ImageField(upload_to="student_photos/", blank=True, null=True)
    qr_code_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.admission_number})"

    def save(self, *args, **kwargs):
        # Generate a unique QR code ID if missing
        if not self.qr_code_id:
            self.qr_code_id = str(uuid.uuid4())[:8]

        # Only generate QR code image if missing
        if not self.qr_code_image:
            qr = qrcode.make(self.qr_code_id)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            filename = f"{self.admission_number}_qr.png"
            self.qr_code_image.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    # ✅ Helper method to check if student has eaten a particular meal today
    def has_eaten(self, meal_type, date=None):
        if not date:
            date = timezone.now().date()
        return FeedingRecord.objects.filter(
            student=self, meal_type=meal_type, date=date
        ).exists()


# ✅ Define Meal Types
MEAL_TYPES = [
    ("breakfast", "Breakfast"),
    ("lunch", "Lunch"),
    ("dinner", "Dinner"),
    ("night_snack", "Night Snack"),
]


class FeedingRecord(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(auto_now_add=True)  # ✅ Auto record serving time
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)

    class Meta:
        unique_together = (
            "student",
            "date",
            "meal_type",
        )  # ✅ Prevents double-feeding

    def __str__(self):
        return f"{self.student.name} - {self.meal_type} on {self.date}"
