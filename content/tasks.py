from pathlib import Path
import subprocess

from django.conf import settings

from content.models import Video


HLS_RESOLUTIONS = {
    '480p': 480,
    '720p': 720,
    '1080p': 1080,
}


def process_video(video_id):
    """Process uploaded video in background."""
    video = Video.objects.get(id=video_id)

    try:
        video.processing_status = Video.ProcessingStatus.PROCESSING
        video.save(update_fields=['processing_status'])

        has_custom_thumbnail = bool(video.thumbnail)
        thumbnail_path = create_thumbnail(video)

        for resolution_name, height in HLS_RESOLUTIONS.items():
            create_hls_stream(video, resolution_name, height)

        create_master_playlist(video)

        video.processing_status = Video.ProcessingStatus.READY
        video.processing_error = ''

        update_fields = ['processing_status', 'processing_error']

        if not has_custom_thumbnail:
            video.thumbnail.name = get_media_relative_path(thumbnail_path)
            update_fields.append('thumbnail')

        video.save(update_fields=update_fields)

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


def create_hls_stream(video, resolution_name, height):
    """Create HLS stream for uploaded video."""
    source_path = Path(video.source_file.path)
    hls_dir = (
        Path(settings.MEDIA_ROOT)
        / 'hls'
        / f'video_{video.id}'
        / resolution_name
    )
    hls_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = hls_dir / 'index.m3u8'
    segment_pattern = hls_dir / 'segment_%03d.ts'

    command = [
        'ffmpeg',
        '-y',
        '-i',
        str(source_path),
        '-vf',
        f'scale=-2:{height}',
        '-c:v',
        'libx264',
        '-c:a',
        'aac',
        '-hls_time',
        '6',
        '-hls_playlist_type',
        'vod',
        '-hls_segment_filename',
        str(segment_pattern),
        str(playlist_path),
    ]

    subprocess.run(command, check=True)
    return playlist_path


def create_master_playlist(video):
    """Create adaptive master playlist."""
    hls_root = (
        Path(settings.MEDIA_ROOT)
        / 'hls'
        / f'video_{video.id}'
    )

    master_path = hls_root / 'master.m3u8'

    content = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=854x480
480p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
720p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/index.m3u8
"""

    with open(master_path, 'w', encoding='utf-8') as file:
        file.write(content)