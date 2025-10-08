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


class EventRegistration(BaseModel):
    event = django.db.models.ForeignKey(
        Event,
        on_delete=django.db.models.CASCADE,
        related_name="registrations",
        verbose_name="Event",
    )
    full_name = django.db.models.CharField(max_length=128, verbose_name="Full Name")
    email = django.db.models.EmailField(verbose_name="Email")
    confirmation_code = django.db.models.CharField(
        max_length=6, verbose_name="Confirmation Code"
    )
    is_confirmed = django.db.models.BooleanField(
        default=False, verbose_name="Confirmed"
    )

    class Meta:
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
        unique_together = ["event", "email"]  # One email per event
        indexes = [
            django.db.models.Index(fields=["event", "email"]),
            django.db.models.Index(fields=["confirmation_code"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.event.name}"
