from django.contrib import admin
from django.utils.html import format_html
from .models import Events  # adjust if your model name/path is different

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('eventid', 'eventname', 'eventdate', 'eventtime', 'eventCreator', 'cover_thumbnail', 'visibility')
    search_fields = ('eventname', 'eventlocation', 'eventdesc')
    list_filter = ('eventdate',)
    readonly_fields = ('image_preview',)  # shown in detail view

    fieldsets = (
        (None, {
            'fields': ('eventname', 'eventdesc')
        }),
        ('Schedule & Location', {
            'fields': ('eventdate', 'eventtime', 'eventlocation')
        }),
        ('Media & Creator', {
            'fields': ('eventCoverPhoto', 'image_preview', 'eventCreator')
        }),
        ('Visibility', {
            'fields': ('visibility',)
        }),
    )

    def image_preview(self, obj):
        """Large preview shown on the change form."""
        if obj and getattr(obj, 'eventCoverPhoto', None):
            return format_html('<img src="{}" style="max-height:250px; max-width:400px;"/>', obj.eventCoverPhoto.url)
        return "No image"
    image_preview.short_description = "Cover preview"

    def cover_thumbnail(self, obj):
        """Small thumbnail shown in list display."""
        if obj and getattr(obj, 'eventCoverPhoto', None):
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.eventCoverPhoto.url)
        return ""
    cover_thumbnail.short_description = "Cover"

    
