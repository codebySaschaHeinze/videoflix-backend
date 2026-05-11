from django.contrib import admin
from django_rq import get_queue

from content.models import Video
from content.tasks import process_video


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

    def save_model(self, request, obj, form, change):
        """Save video and recreate thumbnail if it was removed."""
        super().save_model(request, obj, form, change)

        if change and not obj.thumbnail:
            queue = get_queue('default')
            queue.enqueue(process_video, obj.id)