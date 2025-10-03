import requests
from django.utils import timezone

from .models import SyncResult, SyncSettings
from .serializers import ExternalEventSerializer


class EventProvideClient:
    BASE_URL = "https://events.k3scluster.tech/api/events"

    def get_events(self, changed_at=None):
        """Получение мероприятий из events-provider"""
        params = {}
        if changed_at:
            params["changed_at"] = changed_at.strftime("%Y-%m-%d")

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch events from provider: {str(e)}")

    def sync_events(self, changed_at=None):
        """Синхронизация мероприятий"""
        events_data = self.get_events(changed_at)

        new_count = 0
        updated_count = 0
        errors = []

        for event_data in events_data:
            try:
                serializer = ExternalEventSerializer(data=event_data)
                if serializer.is_valid():
                    event, created = serializer.create_or_update_event()
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                else:
                    errors.append(
                        f"Invalid data for event {event_data.get('id')}: {serializer.errors}"
                    )
            except Exception as e:
                errors.append(
                    f"Error proccessing event {event_data.get('id')}: {str(e)}"
                )

        return new_count, updated_count, errors


class SyncService:
    def __init__(self):
        self.client = EventProvideClient()

    def get_last_sync_date(self):
        """Получение даты последней успешной синхронизации"""
        try:
            last_sync_settings = SyncSettings.objects.get(key="last_successful_sync")
            return timezone.datetime.fromisoformat(last_sync_settings.value)
        except SyncSettings.DoesNotExist:
            pass

        last_sync = SyncResult.objects.filter(is_success=True).first()
        if last_sync:
            return last_sync.finished_at

        return None

    def save_last_sync_date(self, date):
        """Сохранение даты последней синхронизации"""
        SyncSettings.objects.update_or_create(
            key="last_successful_sync",
            defaults={
                "value": date.isoformat(),
                "description": "Date of last successful synchronization",
            },
        )

    def perform_sync(self, full_sync=False):
        """Выполнение синхронизации"""
        sync_result = SyncResult.objects.create()

        try:
            changed_at = None if full_sync else self.get_last_sync_date()
            new_count, updated_count, errors = self.client.sync_events(changed_at)
            sync_result.new_event_count = new_count
            sync_result.updated_events_count = updated_count
            sync_result.finished_at = timezone.now()
            sync_result.is_success = len(errors) == 0
            sync_result.error_message = "\n".join(errors) if errors else ""
            sync_result.save()

            if sync_result.is_success:
                self.save_last_sync_date(sync_result.finished_at)

            return sync_result

        except Exception as e:
            sync_result.finished_at = timezone.now()
            sync_result.is_success = False
            sync_result.error_message = str(e)
            sync_result.save()

            return sync_result
