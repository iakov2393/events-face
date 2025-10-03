from django.contrib import admin

from .models import SyncResult, SyncSettings


class SyncResultAdmin(admin.ModelAdmin):
    # list_display = ['started_at', 'finished_at', 'new_events_count', 'updated_events_count', 'is_success']
    # list_filter = ['is_success', 'started_at']
    # readonly_fields = ['started_at', 'finished_at']
    # search_fields = ['error_message']
    list_display = ["id", "started_at", "finished_at"]
    readonly_fields = ["started_at", "finished_at"]


class SyncSettingsAdmin(admin.ModelAdmin):
    # list_display = ['key', 'value', 'description']
    # search_fields = ['key', 'description']
    list_display = ["key", "value"]


admin.site.register(SyncResult)
admin.site.register(SyncSettings)
