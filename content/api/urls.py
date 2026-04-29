from django.urls import path

from content.api.views import HLSManifestView, HLSMasterPlaylistView, HLSSegmentView, VideoListView


urlpatterns = [
    path('video/', VideoListView.as_view(), name='videolist'),
    path(
    'video/<int:movie_id>/<str:resolution>/index.m3u8',
    HLSManifestView.as_view(),
    name='hls-manifest',
    ),
    path(
    'video/<int:movie_id>/<str:resolution>/<str:segment>/',
    HLSSegmentView.as_view(),
    name='hls-segment',
    ),
    path(
    'video/<int:movie_id>/master.m3u8',
    HLSMasterPlaylistView.as_view(),
    name='hls-master-playlist',
),
]
