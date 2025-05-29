import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import CarPicturesForTrip

@receiver(post_delete, sender=CarPicturesForTrip)
def delete_trip_image_file(sender, instance, **kwargs):
    """
    Deletes the file from storage when the CarPicturesForTrip
    instance is deleted.
    """
    if instance.trip_image:
        instance.trip_image.delete(save=False)