from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(instance, created, **kwargs):
    if not created: return
    UserProfile.objects.create(user=instance)
