from .models import Agent


def trust_current_agent(request):
    """
    Mark the requesting agent as trusted.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    if request.user.is_authenticated():
        if request.agent.is_anonymous:
            request.agent = Agent()

        request.agent.is_trusted = True


def revoke_current_agent(request):
    """
    Revoke trust in the current agent. The next request from the same client
    will come from an untrusted agent.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    if request.user.is_authenticated():
        request.agent = Agent.get_untrusted()


def revoke_other_agents(request):
    """
    Revoke trust in all agents other than the current one.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    if request.user.is_authenticated():
        request.user.agentsettings.serial += 1
        request.user.agentsettings.save()

        request.agent.serial = request.user.agentsettings.serial
