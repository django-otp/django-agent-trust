from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import md5
import json
import logging

from django.core.exceptions import ImproperlyConfigured

from .conf import settings
from .models import SESSION_TOKEN_KEY, Agent, AgentSettings


logger = logging.getLogger(__name__)


class AgentMiddleware(object):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware` to manage
    trusted agents.

    This middleware will set ``request.agent`` to an instance of
    :class:`django_agent_trust.models.Agent`. ``request.agent.is_trusted`` will
    tell you whether the user's agent has been trusted.

    """
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            AgentSettings.objects.ensure_for_user(request.user)
            request.agent = self._load_agent(request)
        else:
            request.agent = Agent.untrusted_agent(request.user)

        response = self.get_response(request)

        agent = getattr(request, 'agent', None)
        if agent and agent.user.is_authenticated:
            self._save_agent(agent, response)

        return response

    def _load_agent(self, request):
        cookie_name = self._cookie_name(request.user.get_username())
        max_age = self._max_cookie_age(request.user.agentsettings)

        # 'e30=' is base64 for '{}'
        encoded = request.get_signed_cookie(cookie_name, default='e30=',
                                            max_age=max_age)

        agent = self._decode_cookie(encoded, request.user)

        if (agent.session is not None) and (agent.session != request.session.get(SESSION_TOKEN_KEY)):
            agent = Agent.untrusted_agent(request.user)

        return agent

    def _decode_cookie(self, encoded, user):
        agent = None

        content = b64decode(encoded.encode('utf-8')).decode('utf-8')
        data = json.loads(content)

        logger.debug('Decoded agent: {0}'.format(data))

        if data.get('username') == user.get_username():
            agent = Agent.from_jsonable(data, user)
            if self._should_discard_agent(agent):
                agent = None

        if agent is None:
            agent = Agent.untrusted_agent(user)

        logger.debug('Loaded agent: username={0}, is_trusted={1}, trusted_at={2}, serial={3}'.format(
            user.get_username(), agent.is_trusted, agent.trusted_at,
            agent.serial)
        )

        return agent

    def _should_discard_agent(self, agent):
        expiration = agent.trust_expiration
        if (expiration is not None) and (expiration < datetime.now()):
            return True

        if agent.serial < agent.user.agentsettings.serial:
            return True

        return False

    def _save_agent(self, agent, response):
        logger.debug('Saving agent: username={0}, is_trusted={1}, trusted_at={2}, serial={3}'.format(
            agent.user.get_username(), agent.is_trusted, agent.trusted_at,
            agent.serial)
        )

        cookie_name = self._cookie_name(agent.user.get_username())
        encoded = self._encode_cookie(agent, agent.user)
        max_age = self._max_cookie_age(agent.user.agentsettings)

        response.set_signed_cookie(cookie_name, encoded, max_age=max_age,
                                   path=settings.AGENT_COOKIE_PATH,
                                   domain=settings.AGENT_COOKIE_DOMAIN,
                                   secure=settings.AGENT_COOKIE_SECURE,
                                   httponly=settings.AGENT_COOKIE_HTTPONLY)

    def _encode_cookie(self, agent, user):
        data = agent.to_jsonable()
        content = json.dumps(data)
        encoded = b64encode(content.encode('utf-8')).decode('utf-8')

        return encoded

    def _cookie_name(self, username):
        suffix = md5(username.encode('utf-8')).hexdigest()[16:]

        return '{0}-{1}'.format(settings.AGENT_COOKIE_NAME, suffix)

    def _max_cookie_age(self, agentsettings):
        """
        Returns the max cookie age based on inactivity limits.
        """
        days = settings.AGENT_INACTIVITY_DAYS

        try:
            int(days) * 86400
        except Exception:
            raise ImproperlyConfigured('AGENT_INACTIVITY_DAYS must be a number.')

        user_days = agentsettings.inactivity_days
        if (user_days is not None) and (user_days < days):
            days = user_days

        return days * 86400
