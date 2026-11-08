from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.student_page, name="student_page"),
    path("all/", views.admin_page, name="admin_page"),
    path(
        "<uuid:complaint_id>/status/",
        views.update_complaint_status,
        name="update_complaint_status",
    ),
    path("leave/<uuid:leave_id>/decide/", views.decide_leave, name="decide_leave"),
]
