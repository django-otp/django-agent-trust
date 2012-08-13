from .models import Agent


def trust_current_agent(request, trust_days=None):
    """
    Mark the requesting agent as trusted for the currently logged-in user. This
    does nothing for anonymous users.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    :param float trust_days: The number of days to trust this agent. ``None``
        for no agent-specific limit.
    """
    if request.user.is_authenticated():
        request.agent = Agent.get_trusted(request.user, trust_days)


def revoke_current_agent(request):
    """
    Revoke trust in the requesting agent for the currently logged-in user.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    request.agent = Agent.get_untrusted(request.user)


def revoke_other_agents(request):
    """
    Revoke trust in all of the logged-in user's agents other than the current
    one. This does nothing for anonymous users.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    if request.user.is_authenticated():
        request.user.agentsettings.serial += 1
        request.user.agentsettings.save()

        request.agent._serial = request.user.agentsettings.serial
