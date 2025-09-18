from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[("Admin", "Admin"), ("Teacher", "Teacher"), ("Staff", "Staff")],
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "is_staff",
            "is_active",
            "role",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove help text from all fields
        for field_name in self.fields:
            self.fields[field_name].help_text = ""
