from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm


@staff_member_required
def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # make them staff by default
            user.save()

            # assign to selected group
            role_name = form.cleaned_data["role"]
            group = Group.objects.get(name=role_name)
            user.groups.add(group)

            return redirect("register_user")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register_user.html", {"form": form})
