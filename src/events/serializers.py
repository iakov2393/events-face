from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Event, EventRegistration, Place


class EventSerializer(serializers.ModelSerializer):
    place_id = serializers.UUIDField(required=False, allow_null=True)
    place_name = serializers.CharField(source="place.name", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "event_date", "status", "place_id", "place_name"]
        read_only_fields = ["id", "status", "place_name"]

    def create(self, validated_data):
        place_id = validated_data.pop("place_id", None)
        place = None

        if place_id:
            try:
                place = Place.objects.get(id=place_id)
            except Place.DoesNotExist:
                raise serializers.ValidationError({"place_id": "Place not found"})

        return Event.objects.create(place=place, **validated_data)


class EventListSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "status", "place_name", "created_at"]


class EventDetailSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "event_date",
            "status",
            "place_name",
            "created_at",
            "updated_at",
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = EventRegistration
        fields = ["event_id", "full_name", "email"]

    def validate_full_name(self, value):
        if len(value) > 128:
            raise serializers.ValidationError(
                "Full name must not exceed 128 characters"
            )
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value.lower()

    def validate(self, data):
        event_id = data.get("event_id")
        email = data.get("email")

        try:
            event = Event.objects.get(id=event_id)
            if event.status != "open":
                raise serializers.ValidationError(
                    {"event_id": "Registration for this event closed"}
                )
        except Event.DoesNotExist:
            raise serializers.ValidationError({"event_id": "Event not found"})

        if EventRegistration.objects.filter(event_id=event_id, email=email).exists():
            raise serializers.ValidationError(
                {"email": "You are already registered for this event"}
            )
        data["event"] = event

        return data
