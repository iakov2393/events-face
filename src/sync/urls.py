from django.urls import path

from . import views

app_name = "sync"

urlpatterns = [
    path("outbox/stats/", views.outbox_stats, name="outbox-stats"),
    path("outbox/health/", views.outbox_health, name="outbox-health"),
]
