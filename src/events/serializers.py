from rest_framework import serializers

from .models import Event, Place


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
