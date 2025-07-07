from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'class_name','admission_number', 'photo' ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter student name'}),
            'class_name': forms.TextInput(attrs={'placeholder': 'Enter class name'}),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'admission_number': forms.TextInput(attrs={'placeholder': 'Enter admission number'}),
        }
        