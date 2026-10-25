from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.HMSLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("profile/", views.edit_profile, name="edit_profile"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path(
        "admin-panel/registrations/<uuid:user_id>/decision/",
        views.decide_registration,
        name="decide_registration",
    ),
]
