from pathlib import Path
import subprocess

from django.conf import settings

from content.models import Video


def process_video(video_id):
    """Process uploaded video in background."""
    video = Video.objects.get(id=video_id)

    try:
        video.processing_status = Video.ProcessingStatus.PROCESSING
        video.save(update_fields=['processing_status'])

        thumbnail_path = create_thumbnail(video)

        video.thumbnail.name = get_media_relative_path(thumbnail_path)
        video.processing_status = Video.ProcessingStatus.READY
        video.processing_error = ''
        video.save(update_fields=['thumbnail', 'processing_status', 'processing_error'])

    except Exception as error:
        video.processing_status = Video.ProcessingStatus.FAILED
        video.processing_error = str(error)
        video.save(update_fields=['processing_status', 'processing_error'])


def create_thumbnail(video):
    """Create thumbnail image from uploaded video."""
    source_path = Path(video.source_file.path)
    thumbnail_dir = Path(settings.MEDIA_ROOT) / 'thumbnails'
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    thumbnail_path = thumbnail_dir / f'video_{video.id}.jpg'

    command = [
        'ffmpeg',
        '-y',
        '-i',
        str(source_path),
        '-ss',
        '00:00:01',
        '-vframes',
        '1',
        str(thumbnail_path),
    ]

    subprocess.run(command, check=True)
    return thumbnail_path

def get_media_relative_path(file_path):
    """Return file path relative to media root."""
    return str(Path(file_path).relative_to(settings.MEDIA_ROOT))