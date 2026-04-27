from django.db import models


class Video(models.Model):
    """Store video metadata."""


    class ProcessingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        READY = 'ready', 'Ready'
        FAILED = 'failed', 'Failed'

    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=50)

    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    source_file = models.FileField(upload_to='videos/')

    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )

    processing_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title