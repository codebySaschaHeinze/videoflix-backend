from rest_framework import serializers

from content.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for video metadata."""


    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields= [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        ]

    def get_thumbnail_url(self, obj):
        """Return absolute thumbnail URL."""
        request = self.context.get('request')

        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        
        if obj.thumbnail:
            return obj.thumbnail.url
        
        return None
    
    