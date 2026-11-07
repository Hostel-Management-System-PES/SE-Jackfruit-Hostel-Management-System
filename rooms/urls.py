from django.urls import path

from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("<uuid:pk>/edit/", views.room_edit, name="room_edit"),
    path("allocate/", views.allocate, name="allocate"),
    path(
        "allocations/<uuid:allocation_id>/deallocate/",
        views.deallocate,
        name="deallocate",
    ),
    path("my-room/", views.my_room, name="my_room"),
]
