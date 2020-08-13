import django.conf


class Settings(object):
    """
    This is a simple class to take the place of the global settings object. An
    instance will contain all of our settings as attributes, with default values
    if they are not specified by the configuration.
    """
    defaults = {
        'AGENT_COOKIE_DOMAIN': None,
        'AGENT_COOKIE_HTTPONLY': True,
        'AGENT_COOKIE_NAME': 'agent-trust',
        'AGENT_COOKIE_PATH': '/',
        'AGENT_COOKIE_SECURE': False,

        'AGENT_LOGIN_URL': django.conf.settings.LOGIN_URL,

        'AGENT_TRUST_DAYS': None,
        'AGENT_INACTIVITY_DAYS': 365,
    }

    def __init__(self):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        for name, default in self.defaults.items():
            value = getattr(django.conf.settings, name, default)
            setattr(self, name, value)

    #
    # Inspired by django.test.TestCase.settings, objects of this class can be
    # used as a context managager to temporarily override settings.
    #
    class ContextManager(object):
        def __init__(self, settings, contextual):
            self.settings = settings
            self.original = dict((k, getattr(settings, k)) for k in contextual)
            self.contextual = contextual

        def __enter__(self):
            for k, v in self.contextual.items():
                setattr(self.settings, k, v)

        def __exit__(self, *args, **kwargs):
            for k, v in self.original.items():
                setattr(self.settings, k, v)

    def __call__(self, **kwargs):
        return self.ContextManager(self, kwargs)


settings = Settings()
