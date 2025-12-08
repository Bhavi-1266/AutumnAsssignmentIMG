from django.contrib import admin
from django.utils.html import format_html
from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'photoid',
        'small_thumb',
        'short_desc',
        'event',
        'uploadedBy',
        'uploadDate',
    )

    list_display_links = ('photoid', 'small_thumb', 'short_desc')

    search_fields = ('photoDesc', 'event__eventname', 'uploadedBy__username')

    list_filter = ('event', 'uploadedBy', 'uploadDate')

    readonly_fields = ('image_preview', 'photoid', 'uploadDate')

    ordering = ('-uploadDate',)

    fieldsets = (
        (None, {
            'fields': ('photoDesc', 'photoFile', 'image_preview')
        }),
        ('Relations', {
            'fields': ('event', 'uploadedBy')
        }),
        ('Metadata', {
            'fields': ('extractedTags', 'photoMeta')
        }),
    )

    # ---------- small thumbnail in list ----------
    def small_thumb(self, obj):
        if obj.photoFile:
            return format_html('<img src="{}" style="height:50px;"/>', obj.photoFile.url)
        return ""
    small_thumb.short_description = "Preview"

    # ---------- description clip ----------
    def short_desc(self, obj):
        if obj.photoDesc:
            return obj.photoDesc[:30] + "..." if len(obj.photoDesc) > 30 else obj.photoDesc
        return ""
    short_desc.short_description = "Description"

    # ---------- large preview on detail page ----------
    def image_preview(self, obj):
        if obj.photoFile:
            return format_html('<img src="{}" style="max-height:350px;"/>', obj.photoFile.url)
        return "No image"
    image_preview.short_description = "Full Preview"
