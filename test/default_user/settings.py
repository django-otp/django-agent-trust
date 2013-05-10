# django-agent-trust test project

from os.path import dirname, join, abspath


def project_path(path):
    return abspath(join(dirname(__file__), path))

DEBUG = True

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_agent_trust',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_agent_trust.middleware.AgentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATE_DIRS = [
    project_path('templates'),
]

SECRET_KEY = 'PWuluw4x48GkT7JDPzlDQsBJC8pjIIiqodW9MuMYcU315YEkGJL41i5qooJsg3Tt'

ROOT_URLCONF = 'django_agent_trust.tests.urls'
