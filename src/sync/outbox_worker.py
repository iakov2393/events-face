import logging
import time

from django.db import transaction
from django.utils import timezone

from .models import OutboxMessage
from .outbox_services import MockMessageProducer

logger = logging.getLogger(__name__)


class OutboxWorker:
    """
    Worker for processing outbox messages
    """

    def __init__(self, producer=None, batch_size=100, poll_interval=1):
        self.producer = producer or MockMessageProducer()
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.running = False
        self.processed_total = 0

    def process_outbox(self):
        """
        Main outbox processing method
        """
        self.running = True
        logger.info("Outbox worker started")
        logger.info(
            "Configuration - Batch size: %s, Poll interval: %ss",
            self.batch_size,
            self.poll_interval,
        )

        while self.running:
            try:
                processed_count, failed_count = self._process_batch()

                if processed_count == 0 and failed_count == 0:
                    logger.debug("No messages to process")
                    time.sleep(self.poll_interval)
                else:
                    self.processed_total += processed_count
                    logger.info(
                        "Batch processed - Success: %s, Failed: %s, Total: %s",
                        processed_count,
                        failed_count,
                        self.processed_total,
                    )
                    time.sleep(1)

            except Exception as e:
                logger.error("Error in outbox worker main loop: %s", e)
                time.sleep(10)

    def _process_batch(self):
        """
        Process batch of messages with transaction and locking
        """
        with transaction.atomic():
            messages = (
                OutboxMessage.objects.filter(sent=False, retry_count__lt=3)
                .select_for_update(skip_locked=True)
                .order_by("created_at")[: self.batch_size]
            )

            logger.debug("Found %s messages to process", len(messages))

            processed_count = 0
            failed_count = 0

            for message in messages:
                try:
                    logger.info(
                        "Processing message %s for topic '%s'",
                        message.id,
                        message.topic,
                    )

                    success = self.producer.send_message(message.topic, message.payload)

                    if success:
                        message.sent = True
                        message.sent_at = timezone.now()
                        message.save()
                        processed_count += 1
                        logger.info("Successfully processed message %s", message.id)
                    else:
                        message.retry_count += 1
                        message.last_retry_at = timezone.now()
                        message.save()
                        failed_count += 1
                        logger.warning(
                            "Failed to send message %s, retry count: %s",
                            message.id,
                            message.retry_count,
                        )

                except Exception as e:
                    logger.error("Error processing message %s: %s", message.id, e)
                    message.retry_count += 1
                    message.last_retry_at = timezone.now()
                    message.error_message = str(e)
                    message.save()
                    failed_count += 1

            return processed_count, failed_count

    def stop(self):
        """
        Stop the worker
        """
        self.running = False
        logger.info("Outbox worker stopped")
