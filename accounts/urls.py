from django.urls import path
from .views import register_user, view_users, edit_user, delete_user


urlpatterns = [
    path("register-user/", register_user, name="register_user"),
    path("users/", view_users, name="view_users"),
    path("users/<int:user_id>/edit/", edit_user, name="edit_user"),
    path("users/<int:user_id>/delete/", delete_user, name="delete_user"),
]
