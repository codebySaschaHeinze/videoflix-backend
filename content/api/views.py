from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from content.api.serializers import VideoSerializer
from content.models import Video
from rest_framework.views import APIView


class VideoListView(ListAPIView):
    """Return available videos."""


    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]


class HLSManifestView(APIView):
    """Return HLS manifest file for a video."""


    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return index.m3u8 for selected video resolution."""
        manifest_path = (
            Path(settings.MEDIA_ROOT)
            / 'hls'
            / f'video_{movie_id}'
            / resolution 
            / 'index.m3u8'
        )

        if not manifest_path.exists():
            raise Http404('Manifest not found.')
        
        return FileResponse(
            open(manifest_path, 'rb'),
            content_type='application/vnd.apple.mpegurl',
        )
    

class HLSSegmentView(APIView):
    """Return HLS segment file for a video."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return selected HLS segment file."""
        segment_path = (
            Path(settings.MEDIA_ROOT)
            / 'hls'
            / f'video_{movie_id}'
            / resolution
            / segment
        )

        if not segment_path.exists():
            raise Http404('Segment not found.')
        
        return FileResponse(
            open(segment_path, 'rb'),
            content_type='video/MP2T',
        )
    

class HLSMasterPlaylistView(APIView):
    """Return HLS master playlist for adaptive streaming."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id):
        """Return master.m3u8 for selected video."""
        master_path = (
            Path(settings.MEDIA_ROOT)
            / 'hls'
            / f'video_{movie_id}'
            / 'master.m3u8'
        )

        if not master_path.exists():
            raise Http404('Master playlist not found.')

        return FileResponse(
            open(master_path, 'rb'),
            content_type='application/vnd.apple.mpegurl',
        )
    

