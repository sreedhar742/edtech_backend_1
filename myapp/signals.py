from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Homework, Notification

@receiver(post_save, sender=Homework)
def create_homework_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.teacher,
            message=f"New homework assigned: {instance.title}",
            homework=instance
        )
