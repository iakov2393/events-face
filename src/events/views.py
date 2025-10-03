from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, Place


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_list_protected(request):
    """
    Защищенный эндпоинт для получения списка событий
    Требует валидный Access Token в заголовке Authorization
    """
    events = Event.objects.select_related("place").all()

    event_data = [
        {
            "id": str(event.id),
            "name": event.name,
            "status": event.status,
            "place": event.place.name if event.place else None,
            "created_at": event.created_at,
        }
        for event in events
    ]

    return Response(
        {
            "events": event_data,
            "count": len(event_data),
            "message": "Successfully retrieved events list",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    Защищенный эндпоинт для создания нового события
    Требует валидный Access Token
    """
    name = request.data.get("name")
    event_date = request.data.get("event_date")
    place_id = request.data.get("place_id")

    if not name or not event_date:
        return Response({"error": "Name and event_date are required"}, status=400)

    try:
        place = None
        if place_id:
            place = Place.objects.get(id=place_id)

        event = Event.objects.create(name=name, event_date=event_date, place=place)

        return Response(
            {
                "event": {
                    "id": str(event.id),
                    "name": event.name,
                    "event_date": event.event_date,
                    "status": event.status,
                    "place": event.place.name if event.place else None,
                }
            },
            status=201,
        )

    except Place.DoesNotExist:
        return Response({"error": "Place not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id):
    """
    Защищенный эндпоинт для получения деталей события
    """
    try:
        event = Event.objects.select_related("place").get(id=event_id)

        return Response(
            {
                "event": {
                    "id": str(event.id),
                    "name": event.name,
                    "event_date": event.event_date,
                    "status": event.status,
                    "place": event.place.name if event.place else None,
                    "created_at": event.created_at,
                    "update_at": event.updated_at,
                }
            }
        )

    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)
