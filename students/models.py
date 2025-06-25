from django.utils import timezone
from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.core.files import File


class Student(models.Model):
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    admission_number = models.CharField(max_length=30, unique=True)
    qr_code_id = models.CharField(max_length=100, unique=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.admission_number})"

    def save(self, *args, **kwargs):
        if not self.qr_code_id:
            self.qr_code_id = str(uuid.uuid4())[:8]  # Generate short unique ID
        super().save(*args, **kwargs)

       # Generate QR code from qr_code_id
        qr = qrcode.make(self.qr_code_id)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        filename = f"{self.admission_number}_qr.png"

        # Save the image to the qr_code_image field
        self.qr_code_image.save(filename, File(buffer), save=False)

        # Save the model again with the image
        super().save(*args, **kwargs)


MEAL_TYPES = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ('night_snack', 'Night Snack'),
]

class FeedingRecord(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)

    class Meta:
        unique_together = ('student', 'date', 'meal_type')  # ✅ No double feeding per meal per day

    def __str__(self):
        return f"{self.student.name} - {self.meal_type} on {self.date}"
    
    
