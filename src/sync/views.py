from rest_framework.decorators import api_view
from rest_framework.response import Response

from .outbox_services import OutboxService


@api_view(["GET"])
def outbox_stats(request):
    """
    API for outbox statistics
    """
    stats = OutboxService().get_outbox_stats()
    return Response(stats)


@api_view(["GET"])
def outbox_health(request):
    """
    Health check for outbox
    """
    stats = OutboxService().get_outbox_stats()

    health_status = {
        "status": "healthy" if stats["pending_messages"] < 100 else "warning",
        "pending_messages": stats["pending_messages"],
        "failed_messages": stats["failed_messages"],
        "message": "Outbox is operating normally"
        if stats["pending_messages"] < 100
        else "High number of pending messages",
    }

    return Response(health_status)
