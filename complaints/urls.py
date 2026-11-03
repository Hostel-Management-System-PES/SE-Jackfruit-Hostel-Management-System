from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.student_page, name="student_page"),
    path("all/", views.admin_page, name="admin_page"),
]
