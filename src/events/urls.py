from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list_protected, name="event_list"),
    path("create/", views.create_event, name="create_event"),
    path("<uuid:event_id>/", views.event_detail, name="event_detail"),
]
