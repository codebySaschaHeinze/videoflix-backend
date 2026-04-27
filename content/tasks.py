from content.models import Video


def process_video(video_id):
    """Process uploaded video in background."""
    video = Video.objects.get(id=video_id)
    video.processing_status = Video.ProcessingStatus.PROCESSING
    video.save(update_fields=['processing_status'])

    video.processing_status = Video.ProcessingStatus.READY
    video.processing_error = ''
    video.save(update_fields=['processing_status', 'processing_error'])