from datetime import datetime, timedelta
from time import mktime

import django.conf
from django.db import models

from .conf import settings


SESSION_TOKEN_KEY = 'django-agent-trust-token'


class AgentSettingsManager(models.Manager):
    def ensure_for_user(self, user):
        """
        Loads a user's AgentSettings instance, creating a default if necessary.
        """
        try:
            user.agentsettings
        except self.model.DoesNotExist:
            user.agentsettings = self.create(user=user)


class AgentSettings(models.Model):
    """
    Agent trust settings for a single user.

    .. attribute:: user

        *OneToOneField*: The :class:`~django.contrib.auth.models.User` (or
        custom user model) this belongs to.

    .. attribute:: trust_days

        *FloatField*: The number of days this user's agents will remain
        trusted. ``None`` for no limit. Default is ``None``.

    .. attribute:: inactivity_days

        *FloatField*: The number of days that may elapse between requests from
        one of this user's agents before trust is revoked. ``None`` for no
        limit. Default is ``None``.
    """
    user = models.OneToOneField(django.conf.settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trust_days = models.FloatField(blank=True, null=True, default=None, help_text="The number of days a agent will remain trusted.")
    inactivity_days = models.FloatField(blank=True, null=True, default=None, help_text="The number of days allowed between requests before a agent's trust is revoked.")
    serial = models.IntegerField(default=0, help_text="Increment this to revoke all previously trusted agents.")

    objects = AgentSettingsManager()

    def __str__(self):
        return "AgentSettings: {0}".format(self.user.get_username())


class Agent(object):
    """
    Objects of this class will be attached to requests as ``request.agent``.
    This is not a database model; it will be serialized into a signed cookie.
    These objects are immutable and should never be instantiated directly. Use
    the APIs below to manipulate trust.
    """
    def __init__(self, user, is_trusted, trusted_at, trust_days, serial, session):
        self._user = user
        self._is_trusted = is_trusted
        self._trusted_at = trusted_at.replace(microsecond=0) if (trusted_at is not None) else None
        self._trust_days = trust_days
        self._serial = serial
        self._session = session

    @classmethod
    def untrusted_agent(cls, user):
        return cls(user, False, None, None, -1, None)

    @classmethod
    def trusted_agent(cls, user, trust_days=None):
        if user.is_anonymous:
            raise ValueError("Can't create a trusted agent for an anonymous user.")

        return cls(user, True, datetime.now(), trust_days, user.agentsettings.serial, None)

    @classmethod
    def session_agent(cls, user, token):
        if user.is_anonymous:
            raise ValueError("Can't create a trusted agent for an anonymous user.")

        return cls(user, True, datetime.now(), None, user.agentsettings.serial, token)

    @property
    def user(self):
        return self._user

    @property
    def is_trusted(self):
        """
        ``True`` if this agent has been marked as trusted.
        """
        return self._is_trusted

    @property
    def is_session(self):
        """
        ``True`` if this agent is only trusted for the current session.
        """
        return (self._session is not None)

    @property
    def trusted_at(self):
        """
        The datetime at which this agent was last explicitly trusted, if any.
        """
        return self._trusted_at

    @property
    def trust_days(self):
        return self._trust_days

    @property
    def serial(self):
        return self._serial

    @property
    def session(self):
        return self._session

    @property
    def trust_expiration(self):
        """
        The datetime at which trust in this agent expires. ``None`` if the
        agent is not trusted or does not expire.
        """
        if not hasattr(self, '_trust_expiration'):
            self._trust_expiration = self._get_trust_expiration()

        return self._trust_expiration

    def _get_trust_expiration(self):
        if (not self.is_trusted) or (self.trusted_at is None):
            return None

        prefs = [d for d in [settings.AGENT_TRUST_DAYS,
                             self.user.agentsettings.trust_days,
                             self.trust_days]
                 if d is not None]

        if len(prefs) > 0:
            expiration = self.trusted_at + timedelta(days=min(prefs))
        else:
            expiration = None

        return expiration

    def to_jsonable(self):
        return {
            'username': self.user.get_username() if hasattr(self.user, 'get_username') else self.user.username,
            'is_trusted': self.is_trusted,
            'trusted_at': self._trusted_at_timestamp(),
            'trust_days': self.trust_days,
            'serial': self.serial,
            'session': self.session,
        }

    def _trusted_at_timestamp(self):
        if self.trusted_at is not None:
            timestamp = int(mktime(self.trusted_at.timetuple()))
        else:
            timestamp = None

        return timestamp

    @classmethod
    def from_jsonable(cls, jsonable, user):
        is_trusted = jsonable.get('is_trusted', False)
        trusted_at = jsonable.get('trusted_at', None)
        trust_days = jsonable.get('trust_days', None)
        serial = jsonable.get('serial', -1)
        session = jsonable.get('session', None)

        if trusted_at is not None:
            trusted_at = datetime.fromtimestamp(trusted_at)

        return cls(user, is_trusted, trusted_at, trust_days, serial, session)
