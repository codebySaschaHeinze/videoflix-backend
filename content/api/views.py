from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from content.api.serializers import VideoSerializer
from content.models import Video


class VideoListView(ListAPIView):
    """Return available videos."""


    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]