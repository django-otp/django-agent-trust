from base64 import b64encode, b64decode
from datetime import datetime, timedelta, MINYEAR
import json
import logging

from django.core.exceptions import ImproperlyConfigured

from .conf import settings
from .models import AgentSettings, Agent


logger = logging.getLogger(__name__)


class AgentMiddleware(object):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware` to manage
    trusted agents.

    This middleware will set ``request.agent`` to an instance of
    :class:`django_agent_trust.models.Agent`. ``request.agent.is_trusted`` will
    tell you whether the user's agent has been trusted.

    To mark the requesting agent trusted for future requests, just set
    ``request.agent.is_trusted`` to ``True``.
    """
    def process_request(self, request):
        try:
            if request.user.is_authenticated():
                AgentSettings.objects.get_or_create(user=request.user)

                request.agent = self._load_agent(request)
            else:
                request.agent = Agent.get_untrusted()
        except:
            request.agent = Agent.get_untrusted()

            if settings.DEBUG:
                raise

        return None

    def process_response(self, request, response):
        if request.user.is_authenticated() and getattr(request, 'agent', None):
            self._save_agent(request, response)

        return response


    def _load_agent(self, request):
        cookie_name = self._cookie_name(request.user.username)
        default = b64encode('{}')
        max_age = self._max_cookie_age(request.user.agentsettings)

        encoded = request.get_signed_cookie(cookie_name, default=default,
            max_age=max_age
        )

        return self._decode_cookie(encoded, request.user.agentsettings)

    def _decode_cookie(self, encoded, agentsettings):
        data = json.loads(b64decode(encoded))

        logger.debug('Decoded agent: {0}'.format(data))

        agent = Agent.from_jsonable(data)

        if (agent.trusted_at is None) or (agent.trusted_at < self._min_trusted_at(agentsettings)):
            agent.is_trusted = False

        if agent.serial < agentsettings.serial:
            agent.is_trusted = False

        logger.debug('Loaded agent: is_trusted={0}, trusted_at={1}, serial={2}'.format(
            agent.is_trusted, agent.trusted_at, agent.serial)
        )

        return agent


    def _save_agent(self, request, response):
        agent = request.agent

        logger.debug('Saving agent: is_trusted={0}, trusted_at={1}, serial={2}'.format(
            agent.is_trusted, agent.trusted_at, agent.serial)
        )

        cookie_name = self._cookie_name(request.user.username)
        encoded = self._encode_agent(agent, request.user.agentsettings)
        max_age = self._max_cookie_age(request.user.agentsettings)

        response.set_signed_cookie(cookie_name, encoded, max_age=max_age,
            path=settings.AGENT_COOKIE_PATH,
            domain=settings.AGENT_COOKIE_DOMAIN,
            secure=settings.AGENT_COOKIE_SECURE,
            httponly=settings.AGENT_COOKIE_HTTPONLY
        )

    def _encode_cookie(self, agent, agentsettings):
        if agent.is_trusted:
            if agent.trusted_at is None:
                agent.trusted_at = datetime.now().replace(microsecond=0)

            if agent.serial < 0:
                agent.serial = agentsettings.serial

        encoded = b64encode(json.dumps(agent.to_jsonable()))

        return encoded


    def _cookie_name(self, username):
        return '{0}-{1}'.format(settings.AGENT_COOKIE_NAME, username)

    def _max_cookie_age(self, agentsettings):
        """
        Returns the max cookie age based on inactivity limits.
        """
        days = settings.AGENT_INACTIVITY_DAYS

        try:
            days * 86400
        except StandardError:
            raise ImproperlyConfigured('AGENT_INACTIVITY_DAYS must be a number.')

        user_days = agentsettings.inactivity_days
        if (user_days is not None) and (user_days < days):
            days = user_days

        return days * 86400

    def _min_trusted_at(self, agentsettings):
        """
        Returns the earliest datetime that we'll accept as a trusted_at value.
        Anything before that has expired.
        """
        prefs = filter(
            lambda d: d is not None, [
                settings.AGENT_TRUST_DAYS,
                agentsettings.trust_days
            ]
        )

        if len(prefs) > 0:
            min_trusted_at = datetime.now() - timedelta(days=min(prefs))
        else:
            min_trusted_at = datetime(MINYEAR, 1, 1)

        return min_trusted_at
