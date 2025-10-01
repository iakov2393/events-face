from django.db import models
import django.db.models
from src.core.models import BaseModel


class Place(BaseModel):
    name = django.db.models.CharField(
        max_length=128,
        verbose_name="Name",
    )

    class Meta:
        verbose_name = "Place"
        verbose_name_plural = "Places"


class EventsStatus(django.db.models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class Event(BaseModel):
    name = django.db.models.CharField(
        max_length=128,
        verbose_name="Name",
    )
    event_date = django.db.models.DateTimeField(
        verbose_name="Event Date",
    )
    status = django.db.models.CharField(
        max_length=10,
        choices=EventsStatus.choices,
        default=EventsStatus.OPEN,
        verbose_name="Status",
    )
    place = django.db.models.ForeignKey(
        Place,
        verbose_name="Place",
        related_name="events",
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            django.db.models.Index(
                ["status", "event_date"], name="event_status_date_idx"
            )
        ]

    def __str__(self):
        return self.name