from django.urls import path

from content.api.views import VideoListView


urlpatterns = [
    path('video/', VideoListView.as_view(), name='videollist'),
]
