from django.urls import path
from .views import register_user, view_users


urlpatterns = [
    path("register-user/", register_user, name="register_user"),
    path("users/", view_users, name="view_users"),
]
