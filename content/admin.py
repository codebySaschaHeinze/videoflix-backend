from django.contrib import admin

from content.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configure video display in Django admin."""

    list_display = (
        'title',
        'category',
        'processing_status',
        'created_at',
        'updated_at',
    )
    list_filter = ('category', 'processing_status')
    search_fields = ('title', 'description')
    readonly_fields = (
        'created_at',
        'updated_at',
        'processing_error',
    )