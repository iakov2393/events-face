import logging
import uuid
from django.utils import timezone

from .models import OutboxMessage

logger = logging.getLogger(__name__)


class OutboxService:
    """
    Service for working with transactional outbox pattern
    """

    def create_message(self, topic, payload):
        """
        Create message in outbox
        """
        message = OutboxMessage.objects.create(
            id=uuid.uuid4(),
            topic=topic,
            payload=payload,
            sent=False
        )
        logger.debug("Created outbox message %s", message.id)
        return message

    def create_event_created_message(self, event):
        """
        Create message for event creation
        """
        payload = {
            "message_id": str(uuid.uuid4()),
            "event_id": str(event.id),
            "event_name": event.name,
            "event_date": self._safe_isoformat(event.event_date),
            "status": event.status,
            "place_id": str(event.place.id) if event.place else None,
            "place_name": event.place.name if event.place else None,
            "created_at": self._safe_isoformat(event.created_at),
            "action": "event_created",
        }

        message = self.create_message("events", payload)
        logger.info("Created event_created message for event %s", event.id)
        return message

    def create_event_updated_message(self, event):
        """
        Create message for event update
        """
        payload = {
            "message_id": str(uuid.uuid4()),
            "event_id": str(event.id),
            "event_name": event.name,
            "event_date": self._safe_isoformat(event.event_date),
            "status": event.status,
            "place_id": str(event.place.id) if event.place else None,
            "place_name": event.place.name if event.place else None,
            "updated_at": self._safe_isoformat(event.updated_at),
            "action": "event_updated",
        }

        message = self.create_message("events", payload)
        logger.info("Created event_updated message for event %s", event.id)
        return message

    def _safe_isoformat(self, date_value):
        """
        Safely convert date to ISO format string
        """
        if hasattr(date_value, 'isoformat'):
            return date_value.isoformat()
        return str(date_value)

    def get_pending_messages(self, batch_size=100):
        """
        Get unsent messages from outbox
        """
        return OutboxMessage.objects.filter(sent=False).order_by("created_at")[:batch_size]

    def mark_as_sent(self, message):
        """
        Mark message as sent
        """
        message.sent = True
        message.sent_at = timezone.now()
        message.save(update_fields=["sent", "sent_at"])

    def process_pending_messages(self, batch_size=100):
        """
        Process pending outbox messages
        """
        producer = MockMessageProducer()
        messages = self.get_pending_messages(batch_size)
        processed_count = 0

        for message in messages:
            try:
                success = producer.send_message(message.topic, message.payload)
                if success:
                    self.mark_as_sent(message)
                    processed_count += 1
                    logger.info("Message %s sent successfully", message.id)
                else:
                    logger.error("Failed to send message %s", message.id)
            except Exception as e:
                logger.error("Error sending message %s: %s", message.id, str(e))

        return processed_count

    def get_outbox_stats(self):
        """
        Get outbox statistics
        """
        total = OutboxMessage.objects.count()
        sent = OutboxMessage.objects.filter(sent=True).count()
        pending = OutboxMessage.objects.filter(sent=False).count()
        failed = OutboxMessage.objects.filter(sent=False, retry_count__gte=3).count()

        return {
            'total_messages': total,
            'sent_messages': sent,
            'pending_messages': pending,
            'failed_messages': failed
        }


class MockMessageProducer:
    """
    Mock producer for message sending (instead of real Kafka/RabbitMQ)
    """

    def send_message(self, topic, payload):
        """
        Mock message sending - just log instead of real delivery
        """
        logger.info("Message would be sent to '%s': %s", topic, payload)
        return True