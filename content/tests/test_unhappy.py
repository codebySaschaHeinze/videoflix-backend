from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from content.models import Video


User = get_user_model()


@override_settings(MEDIA_ROOT='/tmp/videoflix_test_media')
class ContentUnhappyTests(APITestCase):
    """Test failed content endpoint flows."""

    def setUp(self):
        """Set up authenticated user and video."""
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='user@example.com',
            password='Test12345!',
            is_active=True,
        )

        self.video = Video.objects.create(
            title='Test Video',
            description='A test video description.',
            category='Drama',
            source_file=SimpleUploadedFile(
                'test.mp4',
                b'fake video content',
                content_type='video/mp4',
            ),
        )

    def test_video_list_without_authentication_fails(self):
        """Test unauthenticated user cannot fetch video list."""
        response = self.client.get('/api/video/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_hls_manifest_returns_404(self):
        """Test missing HLS manifest returns 404."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/video/{self.video.id}/720p/index.m3u8'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_hls_segment_returns_404(self):
        """Test missing HLS segment returns 404."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/video/{self.video.id}/720p/segment_000.ts/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_hls_manifest_without_authentication_fails(self):
        """Test unauthenticated user cannot fetch HLS manifest."""
        self.create_test_file(
            f'hls/video_{self.video.id}/720p/index.m3u8',
            '#EXTM3U\n',
        )

        response = self.client.get(
            f'/api/video/{self.video.id}/720p/index.m3u8'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_hls_segment_without_authentication_fails(self):
        """Test unauthenticated user cannot fetch HLS segment."""
        self.create_test_file(
            f'hls/video_{self.video.id}/720p/segment_000.ts',
            b'fake segment content',
            binary=True,
        )

        response = self.client.get(
            f'/api/video/{self.video.id}/720p/segment_000.ts/'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def create_test_file(self, relative_path, content, binary=False):
        """Create a temporary media file for endpoint tests."""
        file_path = Path('/tmp/videoflix_test_media') / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'wb' if binary else 'w'

        with open(file_path, mode) as test_file:
            test_file.write(content)

        return file_path