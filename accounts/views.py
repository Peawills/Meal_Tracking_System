# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group, User
from .forms import CustomUserCreationForm
from django.shortcuts import get_object_or_404


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


@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.is_active = "is_active" in request.POST
        user.is_staff = "is_staff" in request.POST

        # Update group
        role = request.POST.get("role")
        user.groups.clear()
        if role:
            group = Group.objects.get(name=role)
            user.groups.add(group)

        user.save()
        messages.success(request, f"✅ User '{user.username}' updated successfully.")
        return redirect("view_users")

    return render(
        request,
        "accounts/edit_user.html",
        {"user_obj": user, "groups": Group.objects.all()},
    )


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, f"🗑️ User deleted successfully.")
        return redirect("view_users")
    return render(request, "accounts/delete_user.html", {"user_obj": user})
