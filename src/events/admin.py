from django.contrib import admin

from .models import Event, Place


class PlaceAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    list_filter = ["created_at"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "event_date", "status", "place", "created_at"]
    list_filter = ["status", "event_date", "place"]
    search_fields = ["name"]
    date_hierarchy = "event_date"
    raw_id_fields = ["place"]


admin.site.register(Place, PlaceAdmin)
admin.site.register(Event, EventAdmin)
