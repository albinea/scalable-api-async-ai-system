from django.urls import path

from .views import (
    chat,
    task_status,
    health,
)

urlpatterns = [
    path("chat/", chat),
    path("tasks/<str:task_id>/", task_status),
    path("health/", health),
]