import logging
import signal
from django.core.management.base import BaseCommand

from src.sync.outbox_services import MockMessageProducer
from src.sync.outbox_worker import OutboxWorker

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run outbox message processing worker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of messages to process in one batch",
        )
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=1.0,
            help="Sleep interval between batches in seconds",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting outbox worker...")

        worker = OutboxWorker(
            producer=MockMessageProducer(),
            batch_size=options["batch_size"],
            poll_interval=options["poll_interval"]
        )

        def signal_handler(signum, frame):
            self.stdout.write("Received shutdown signal...")
            worker.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            worker.process_outbox()
        except KeyboardInterrupt:
            self.stdout.write("Outbox worker stopped by user")
        except Exception as e:
            logger.error("Outbox worker error: %s", e)
            raise