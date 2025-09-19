# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User


@staff_member_required
def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            role_name = form.cleaned_data["role"]

            user = form.save(commit=False)
            user.is_active = True  # allow login

            # ✅ Automatically set staff for Admins only
            if role_name == "Admin":
                user.is_staff = True
            else:
                user.is_staff = False

            user.save()

            # assign user to the selected group
            group = Group.objects.get(name=role_name)
            user.groups.add(group)

            messages.success(
                request, f"✅ User '{user.username}' created successfully."
            )
            return redirect("register_user")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register_user.html", {"form": form})


@staff_member_required
def view_users(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "accounts/view_users.html", {"users": users})
