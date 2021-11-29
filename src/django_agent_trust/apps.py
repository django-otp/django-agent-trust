from django.apps import AppConfig


class DefaultConfig(AppConfig):
    name = 'django_agent_trust'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from . import signals  # noqa
