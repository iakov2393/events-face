from rest_framework import serializers

from src.events.models import Event, Place


class ExternalPlaceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class ExternalEventSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    event_date = serializers.DateTimeField()
    status = serializers.CharField()
    place = ExternalPlaceSerializer()
    changed_at = serializers.DateTimeField()

    def create_or_update_event(self):
        event_data = self.validated_data
        place_data = event_data.pop("place")

        place, _ = Place.object.get_or_create(
            id=place_data["id"], defaults={"name": place_data["name"]}
        )

        event, created = Event.object.get_or_create(
            id=event_data["id"],
            defaults={
                "name": event_data["name"],
                "event_date": event_data["event_date"],
                "status": event_data["status"],
                "place": place,
            },
        )

        return event, created
