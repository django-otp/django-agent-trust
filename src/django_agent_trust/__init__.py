from random import randrange


def trust_agent(request, trust_days=None):
    """
    Mark the requesting agent as trusted for the currently logged-in user. This
    does nothing for anonymous users.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    :param float trust_days: The number of days to trust this agent. ``None``
        for no agent-specific limit.
    """
    from .models import Agent

    if request.user.is_authenticated:
        request.agent = Agent.trusted_agent(request.user, trust_days)


def trust_session(request):
    """
    Mark the requesting agent as trusted in the context of the current session;
    when the session ends, the agent's trust will be revoked. This replaces any
    agent trust that already exists. All expiration settings and future
    revocations still apply. This does nothing for anonymous users.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    from .models import SESSION_TOKEN_KEY, Agent

    if request.user.is_authenticated:
        # We need a token to link this agent to the current session. It's
        # strictly internal, so it doesn't have to be cryptographically sound,
        # just probabalistically unique.
        token = randrange(2 ** 32)

        request.session[SESSION_TOKEN_KEY] = token
        request.agent = Agent.session_agent(request.user, token)


def revoke_agent(request):
    """
    Revoke trust in the requesting agent for the currently logged-in user.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    from .models import Agent

    request.agent = Agent.untrusted_agent(request.user)


def revoke_other_agents(request):
    """
    Revoke trust in all of the logged-in user's agents other than the current
    one. This does nothing for anonymous users.

    :param request: The current request.
    :type request: :class:`~django.http.HttpRequest`
    """
    if request.user.is_authenticated:
        request.user.agentsettings.serial += 1
        request.user.agentsettings.save()

        request.agent._serial = request.user.agentsettings.serial
