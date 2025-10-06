import logging
import uuid

from django.utils import timezone

from .models import OutboxMessage

logger = logging.getLogger(__name__)


class OutboxService:
    def create_message(self, topic, payload):
        """
        Создание сообщения в outbox
        """
        return OutboxMessage.objects.create(
            id=uuid.uuid4(), topic=topic, payload=payload, sent=False
        )

    def create_event_created_message(self, event):
        """
        Создание сообщения о создании мероприятия
        """
        payload = {
            "message_id": str(uuid.uuid4()),
            "event_id": str(event.id),
            "event_name": event.name,
            "event_date": event.event_date.isoformat(),
            "status": event.status,
            "place_id": str(event.place.id) if event.place else None,
            "place_name": event.place.name if event.place else None,
            "created_at": event.created_at.isoformat(),
            "action": "event_created",
        }

        return self.create_message("events", payload)

    def create_event_updated_message(self, event):
        """
        Создание сообщения об обновлении мероприятия
        """
        payload = {
            "message_id": str(uuid.uuid4()),
            "event_id": str(event.id),
            "event_name": event.name,
            "event_date": event.event_date.isoformat(),
            "status": event.status,
            "place_id": str(event.place.id) if event.place else None,
            "place_name": event.place.name if event.place else None,
            "updated_at": event.updated_at.isoformat(),
            "action": "event_updated",
        }

        return self.create_message("events", payload)

    def get_pending_messages(self, batch_size=100):
        """
        Получение непрочитанных сообщений
        """
        return OutboxMessage.objects.filter(sent=False).order_by("created_at")[
            :batch_size
        ]

    def mark_as_sent(self, message):
        """
        Пометка сообщения как отправленного
        """
        message.sent = True
        message.sent_at = timezone.now()
        message.save(update_fields=["sent", "sent_at"])

    def process_pending_messages(self, batch_size=100):
        """
        Обработка непрочитанных сообщений
        """
        producer = MockMessageProducer()
        messages = self.get_pending_messages(batch_size)

        for message in messages:
            try:
                success = producer.send_message(message.topic, message.payload)
                if success:
                    self.mark_as_sent(message)
                    logger.info(f"OUTBOX: Message {message.id} sent successfully")
                else:
                    logger.error(f"OUTBOX: Failed to send message {message.id}")
            except Exception as e:
                logger.error(f"OUTBOX: Error sending message {message.id}: {str(e)}")

        return len(messages)


class MockMessageProducer:
    """
    Mock продюсер - вместо реальной отправки в Kafka/RabbitMQ
    """

    def send_message(self, topic, payload):
        """
        Вместо реальной отправки - просто логируем
        """
        logger.info(f"OUTBOX: Message would be sent to '{topic}': {payload}")
        return True
