from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.sync.outbox_services import OutboxService

from .models import Event
from .serializers import EventDetailSerializer, EventListSerializer, EventSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_list_protected(request):
    """
    Protected endpoint for retrieving events list
    Requires valid Access Token in Authorization header
    """
    events = Event.objects.select_related("place").all()
    serializer = EventListSerializer(events, many=True)

    return Response({"events": serializer.data, "count": len(serializer.data)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id):
    """
    Protected endpoint for retrieving event details
    """
    try:
        event = Event.objects.select_related("place").get(id=event_id)
        serializer = EventDetailSerializer(event)

        return Response({"event": serializer.data})

    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    Protected endpoint for creating new event with outbox
    """
    serializer = EventSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            event = serializer.save()
            OutboxService().create_event_created_message(event)

            return Response(
                {
                    "message": "Event created successfully",
                    "event": EventSerializer(event).data,
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception:
        return Response(
            {"error": "Failed to create event"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_event(request, event_id):
    """
    Protected endpoint for updating event with outbox
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(event, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            updated_event = serializer.save()
            OutboxService().create_event_updated_message(updated_event)

            return Response(
                {
                    "message": "Event updated successfully",
                    "event": EventSerializer(updated_event).data,
                }
            )

    except Exception:
        return Response(
            {"error": "Failed to update event"}, status=status.HTTP_400_BAD_REQUEST
        )
