from django.urls import path

from content.api.views import HLSManifestView, VideoListView


urlpatterns = [
    path('video/', VideoListView.as_view(), name='videollist'),
    path(
    'video/<int:movie_id>/<str:resolution>/index.m3u8',
    HLSManifestView.as_view(),
    name='hls-manifest',
)
]
