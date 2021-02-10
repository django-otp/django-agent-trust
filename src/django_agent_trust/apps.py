from django.apps import AppConfig


class DefaultConfig(AppConfig):
    name = 'django_agent_trust'

    def ready(self):
        from . import signals  # noqa
