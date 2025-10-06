import logging
import time

from django.db import transaction
from django.utils import timezone

from .models import OutboxMessage
from .outbox_services import MockMessageProducer

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, producer=None, batch_size=100):
        self.producer = producer or MockMessageProducer()
        self.batch_size = batch_size
        self.running = False

    def process_outbox(self):
        """
        Основной метод outbox сообщений
        """
        self.running = True
        logger.info("Outbox worker started")

        while self.running:
            try:
                processed_count = self._process_batch()

                if processed_count == 0:
                    time.sleep(5)
                else:
                    logger.info(f"Processed {processed_count} outbox messages")
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error in outbox worker: {e}")
                time.sleep(10)

    def _process_batch(self):
        """
        Обработка батча сообщений
        """
        with transaction.atomic():
            # Теперь используем поле sent
            messages = (
                OutboxMessage.objects.filter(sent=False)
                .select_for_update(skip_locked=True)
                .order_by("created_at")[: self.batch_size]
            )

            processed_count = 0

            for message in messages:
                try:
                    success = self.producer.send_message(message.topic, message.payload)

                    if success:
                        message.sent = True
                        message.sent_at = timezone.now()
                        message.save()
                        processed_count += 1
                        logger.debug(f"Processed outbox message {message.id}")

                except Exception as e:
                    logger.error(f"Failed to process message {message.id}: {e}")

            return processed_count

    def stop(self):
        """
        Остановка воркера
        """
        self.running = False
        logger.info("Outbox worker stopped")
