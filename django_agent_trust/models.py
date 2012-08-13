from datetime import datetime
from time import mktime

from django.db import models


class AgentSettings(models.Model):
    """
    Agent trust settings for a single user.

    .. attribute:: user

        *OneToOneField*: The :class:`~django.contrib.auth.models.User` this
        belongs to.

    .. attribute:: trust_days

        *FloatField*: The number of days this user's agents will remain
        trusted. ``None`` for no limit. Default is ``None``.

    .. attribute:: inactivity_days

        *FloatField*: The number of days that may elapse between requests from
        one of this user's agents before trust is revoked. ``None`` for no
        limit. Default is ``None``.

    .. attribute:: serial

        *IntegerField*: A serial number that gets incremented every time the
        user revokes previously trusted agents. Cookies with old serial numbers
        are not trusted.
    """
    user = models.OneToOneField('auth.User')
    trust_days = models.FloatField(blank=True, null=True, default=None, help_text="The number of days a agent will remain trusted.")
    inactivity_days = models.FloatField(blank=True, null=True, default=None, help_text="The number of days allowed between requests before a agent's trust is revoked.")
    serial = models.IntegerField(default=0, help_text="Increment this to revoke all previously trusted agents.")


class Agent(object):
    """
    Objects of this type will be attached to requests as ``request.agent``.
    This is not a database model; it will be serialized into a signed cookie.

    If ``is_trusted`` is ``False``, the other fields may still be set to
    indicate trust that has expired or been revoked.

    :param bool is_trusted: ``True`` if this agent is trusted by the user.
    :param datetime trusted_at: When this agent was originally trusted.
    :param int serial: The value of
        :attr:`~otp_agents.models.AgentSettings.serial` at the time this
        agent was trusted.
    """
    is_anonymous = False

    def __init__(self, is_trusted=False, trusted_at=None, serial=-1):
        self._is_trusted = is_trusted
        self.trusted_at = trusted_at
        self.serial = serial

    @classmethod
    def get_untrusted(cls):
        return cls()

    @property
    def is_trusted(self):
        return self._is_trusted

    @is_trusted.setter
    def is_trusted(self, is_trusted):
        if is_trusted and not self._is_trusted:
            self.trusted_at = datetime.now()
            self.serial = -1

        self._is_trusted = is_trusted

    def to_jsonable(self):
        trusted_at = int(mktime(self.trusted_at.timetuple())) if (self.trusted_at is not None) else None

        return {
            'is_trusted': self.is_trusted,
            'trusted_at': trusted_at,
            'serial': self.serial,
        }

    @classmethod
    def from_jsonable(cls, jsonable):
        is_trusted = jsonable.get('is_trusted', False)
        trusted_at = jsonable.get('trusted_at', None)
        serial = jsonable.get('serial', -1)

        if trusted_at is not None:
            trusted_at = datetime.fromtimestamp(trusted_at)

        return cls(is_trusted, trusted_at, serial)


class AnonymousAgent(object):
    """
    A dummy agent for anonymous users.
    """
    is_anonymous = True
    is_trusted = False
    trusted_at = None
    serial = -1
