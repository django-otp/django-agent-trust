from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AgentSettings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def init_agent_settings(sender, instance, created=False, raw=False, **kwargs):
    if instance and created and (not raw):
        AgentSettings.objects.ensure_for_user(instance)
