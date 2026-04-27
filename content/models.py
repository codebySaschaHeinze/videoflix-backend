from django.db import models


class Video(models.Model):
    """Store video metadata"""

    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=50)

    thumbnail = models.ImageField(
        upload_to='thumbnails/',
    )

    source_file = models.FileField(
        upload_to='videos/',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title