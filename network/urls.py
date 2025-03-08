
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_post", views.add_new_post, name="add_new_post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit_post, name="edit"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("delete/<int:post_id>", views.delete_post, name="delete_post"),
    path("post/<int:post_id>/comment/", views.comment, name="comment"),
]
