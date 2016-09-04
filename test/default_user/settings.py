# django-agent-trust test project

from os.path import dirname, join, abspath


def project_path(path):
    return abspath(join(dirname(__file__), path))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_agent_trust',
]

# Django <1.10
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_agent_trust.middleware.AgentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Django >=1.10
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_agent_trust.middleware.AgentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            project_path('templates'),
        ]
    },
]

TEMPLATE_DIRS = [
    project_path('templates'),
]

SECRET_KEY = 'PWuluw4x48GkT7JDPzlDQsBJC8pjIIiqodW9MuMYcU315YEkGJL41i5qooJsg3Tt'

ROOT_URLCONF = 'django_agent_trust.test.urls'
