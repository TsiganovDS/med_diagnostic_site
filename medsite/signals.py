from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from medsite.models import Doctor

User = get_user_model()


@receiver(post_save, sender=get_user_model())
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.is_active:
        Doctor.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_doctor_profile(sender, instance, **kwargs):
    if instance.is_staff:
        try:
            instance.doctor_profile.save()
        except Doctor.DoesNotExist:
            Doctor.objects.create(user=instance)
