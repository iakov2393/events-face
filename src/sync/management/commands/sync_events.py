from django.core.management.base import BaseCommand

from src.sync.services import SyncService


class Command(BaseCommand):
    help = "Synchronize events with events-provider service"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Perform full synchronization of all events",
        )

    def handle(self, *args, **options):
        sync_service = SyncService()

        self.stdout.write("Starting events synchronization...")

        if options["all"]:
            self.stdout.write("Performing full synchronization...")
            result = sync_service.perform_sync(full_sync=True)
        else:
            self.stdout.write("Performing incremental synchronization...")
            result = sync_service.perform_sync(full_sync=False)

        if result.is_success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Synchronization completed successfully! "
                    f"New: {result.new_events_count}, "
                    f"Updated: {result.updated_events_count}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"Synchronization failed: {result.error_message}")
            )
