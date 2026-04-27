import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from content.models import Video
from content.tasks import process_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Start video processing after a new video was created."""
    if created:
        queue = django_rq.get_queue('default')
        queue.enqueue(process_video, instance.id)