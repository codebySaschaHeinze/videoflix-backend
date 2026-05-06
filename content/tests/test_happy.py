import shutil

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from content.models import Video


User = get_user_model()


@override_settings(MEDIA_ROOT='/tmp/videoflix_test_media')
class ContentHappyTests(APITestCase):
    """Test successful content endpoints."""

    def setUp(self):
        """Set up authenticated user and video."""
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='user@example.com',
            password='Test12345!',
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)

        self.video = Video.objects.create(
            title='Test Video',
            description='A test video description.',
            category='Drama',
            processing_status=Video.ProcessingStatus.READY,
            source_file=SimpleUploadedFile(
                'test.mp4',
                b'fake video content',
                content_type='video/mp4',
            ),
        )

    def test_video_list_returns_videos(self):
        """Test authenticated user can fetch video list."""
        response = self.client.get('/api/video/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], self.video.title)
        self.assertEqual(response.data[0]['description'], self.video.description)
        self.assertEqual(response.data[0]['category'], self.video.category)
        self.assertIn('thumbnail_url', response.data[0])

    def test_hls_manifest_returns_playlist(self):
        """Test HLS manifest endpoint returns playlist file."""
        manifest_path = self.create_test_file(
            f'hls/video_{self.video.id}/720p/index.m3u8',
            '#EXTM3U\n#EXTINF:6.0,\nsegment_000.ts\n',
        )

        response = self.client.get(
            reverse(
                'hls-manifest',
                kwargs={
                    'movie_id': self.video.id,
                    'resolution': '720p',
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.apple.mpegurl',
        )
        self.assertTrue(manifest_path.exists())

    def test_hls_segment_returns_video_segment(self):
        """Test HLS segment endpoint returns segment file."""
        segment_path = self.create_test_file(
            f'hls/video_{self.video.id}/720p/segment_000.ts',
            b'fake segment content',
            binary=True,
        )

        response = self.client.get(
            reverse(
                'hls-segment',
                kwargs={
                    'movie_id': self.video.id,
                    'resolution': '720p',
                    'segment': 'segment_000.ts',
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/MP2T')
        self.assertTrue(segment_path.exists())

    def create_test_file(self, relative_path, content, binary=False):
        """Create a temporary media file for endpoint tests."""
        file_path = Path('/tmp/videoflix_test_media') / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'wb' if binary else 'w'

        with open(file_path, mode) as test_file:
            test_file.write(content)

        return file_path
    
    def tearDown(self):
        """Remove temporary test media files."""
        shutil.rmtree('/tmp/videoflix_test_media', ignore_errors=True)