from django.contrib import admin
from .models import Student, FeedingRecord
from django.utils.html import format_html

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_name', 'admission_number', 'show_qr_code')
    search_fields = ('name', 'admission_number')
    

    def show_qr_code(self, obj):
        if obj.qr_code_image:
            return format_html('<img src="{}" width="50" height="50"/>', obj.qr_code_image.url)
        return "No QR"
    show_qr_code.short_description = "QR Code"
    

admin.site.register(Student, StudentAdmin )


class FeedingRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_name', 'meal_type', 'date', 'time')
    list_filter = ('date', 'class_name', 'meal_type')
    search_fields = ('student__name', 'student__admission_number')
    

admin.site.register(FeedingRecord, FeedingRecordAdmin)

