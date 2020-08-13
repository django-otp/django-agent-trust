from functools import wraps

from django.contrib.auth.decorators import user_passes_test

from .conf import settings


def trusted_agent_required(view=None, redirect_field_name='next', login_url=None):
    """
    Similar to :func:`~django.contrib.auth.decorators.login_required`, but
    requires ``request.agent.is_trusted`` to be true. This will frequently be
    used in conjunction with login_required, unless you're allowing trusted
    agents to bypass authentication.

    The default value for ``login_url`` is :setting:`AGENT_LOGIN_URL`.
    """
    if login_url is None:
        login_url = settings.AGENT_LOGIN_URL

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            enforcer = user_passes_test(lambda u: request.agent.is_trusted,
                                        redirect_field_name=redirect_field_name,
                                        login_url=login_url)

            return enforcer(view_func)(request, *args, **kwargs)

        return _wrapped_view

    return decorator(view) if (view is not None) else decorator
