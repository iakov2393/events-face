import uuid

import django.db.models


class BaseModel(django.db.models.Model):
    id = django.db.models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    updated_at = django.db.models.DateTimeField(
        verbose_name="Updated At",
        auto_now=True,
    )
    created_at = django.db.models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True,
    )

    class Meta:
        abstract = True
