from django.db.models.signals import post_save
from django.dispatch import receiver

from .jobs import index_object
from .models import Comic, Issue, Creator


@receiver(post_save, sender=Creator)
@receiver(post_save, sender=Comic)
@receiver(post_save, sender=Issue)
def object_changed(sender, instance, created, **kwargs):
    if created:
        index_object.delay(sender, instance)
