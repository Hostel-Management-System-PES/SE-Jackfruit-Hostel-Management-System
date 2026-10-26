from django.urls import path

from . import views

app_name = "fees"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("student/<uuid:student_id>/", views.student_detail, name="student_detail"),
]
