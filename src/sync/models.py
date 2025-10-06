import uuid

from django.db import models


class SyncResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Started at")
    finished_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Finished at"
    )
    new_events_count = models.PositiveIntegerField(
        default=0, verbose_name="New events count"
    )
    updated_events_count = models.PositiveIntegerField(
        default=0, verbose_name="Updated events count"
    )
    is_success = models.BooleanField(default=True, verbose_name="Success")
    error_message = models.TextField(blank=True, verbose_name="Error message")

    class Meta:
        verbose_name = "Sync Result"
        verbose_name_plural = "Sync Results"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Sync at {self.started_at}"


class SyncSettings(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Key")
    value = models.TextField(verbose_name="Value")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Sync Setting"
        verbose_name_plural = "Sync Settings"

    def __str__(self):
        return self.key


class OutboxMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255, verbose_name="Topic")
    payload = models.JSONField(verbose_name="Payload")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    sent = models.BooleanField(default=False, verbose_name="Sent")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Sent at")

    class Meta:
        verbose_name = "Outbox Message"
        verbose_name_plural = "Outbox Messages"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["sent", "created_at"])]

    def __str__(self):
        return f"{self.topic} - {self.created_at}"
