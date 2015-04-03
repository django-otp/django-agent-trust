from datetime import datetime, timedelta

import django
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import six
if django.VERSION < (1, 7):
    from django.utils import unittest
else:
    import unittest

from .conf import settings
from .decorators import trusted_agent_required
from .models import Agent, AgentSettings
from .middleware import AgentMiddleware


now = lambda: datetime.now().replace(microsecond=0)


@unittest.skipIf(django.VERSION < (1, 4), 'Requires Django 1.4')
class AgentTrustTestCase(TestCase):
    """
    Base class with some custom-user-aware utilities.
    """
    @classmethod
    def setUpClass(cls):
        super(AgentTrustTestCase, cls).setUpClass()

        try:
            from django.contrib.auth import get_user_model
        except ImportError:
            from django.contrib.auth.models import User
            cls.User = User
            cls.User.get_username = lambda self: self.username
            cls.USERNAME_FIELD = 'username'
        else:
            cls.User = get_user_model()
            cls.USERNAME_FIELD = cls.User.USERNAME_FIELD

    def create_user(self, username, password):
        """
        Try to create a user, honoring the custom user model, if any. This may
        raise an exception if the user model is too exotic for our purposes.
        """
        return self.User.objects.create_user(username, password=password)


class AgentCodingTestCase(AgentTrustTestCase):
    """
    Tests as much of the middleware as possible without the request/response
    cycle. Any tests that need to manipulate the date will be at this level.
    """
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'alice')
            AgentSettings.objects.create(user=self.alice)
            self.bob = self.create_user('bob', 'bob')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")

        self.middleware = AgentMiddleware()

    @property
    def agentsettings(self):
        return self.alice.agentsettings

    def test_coverage(self):
        six.u(str(self.agentsettings))

    def test_trust_anonymous(self):
        with self.assertRaises(Exception):
            Agent.trusted_agent(AnonymousUser())

    def test_session_anonymous(self):
        with self.assertRaises(Exception):
            Agent.session_agent(AnonymousUser(), 0)

    def test_untrusted(self):
        agent = self._roundtrip_agent(Agent.untrusted_agent(self.alice))

        self.assertTrue(not agent.is_trusted)
        self.assertTrue(not agent.is_session)
        self.assertEqual(agent.trusted_at, None)
        self.assertEqual(agent.serial, -1)

    def test_trusted(self):
        trusted_at = now()

        agent = self._roundtrip(True, trusted_at, None, 1, None)

        self.assertTrue(agent.is_trusted)
        self.assertTrue(not agent.is_session)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_global_only(self):
        trusted_at = now() - timedelta(days=7)

        with settings(AGENT_TRUST_DAYS=5):
            agent = self._roundtrip(True, trusted_at, None, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_user_only(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 5

        agent = self._roundtrip(True, trusted_at, None, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_agent_only(self):
        trusted_at = now() - timedelta(days=7)

        agent = self._roundtrip(True, trusted_at, 5, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_global_precedence(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 14

        with settings(AGENT_TRUST_DAYS=5):
            agent = self._roundtrip(True, trusted_at, 14, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_user_precedence(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 5

        with settings(AGENT_TRUST_DAYS=14):
            agent = self._roundtrip(True, trusted_at, 14, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_agent_precedence(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 14

        with settings(AGENT_TRUST_DAYS=14):
            agent = self._roundtrip(True, trusted_at, 5, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_expired_none(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 14

        with settings(AGENT_TRUST_DAYS=14):
            agent = self._roundtrip(True, trusted_at, 14, 1, None)

        self.assertTrue(agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_revoked(self):
        trusted_at = now()
        self.agentsettings.serial = 2

        agent = self._roundtrip(True, trusted_at, None, 1, None)

        self.assertTrue(not agent.is_trusted)

    def test_session(self):
        agent = self._roundtrip(True, now(), None, 1, '1234')

        self.assertTrue(agent.is_trusted)
        self.assertTrue(agent.is_session)

    def test_cross_user(self):
        AgentSettings.objects.get_or_create(user=self.bob)

        agent = Agent.trusted_agent(self.alice)
        encoded = self.middleware._encode_cookie(agent, self.alice)
        agent = self.middleware._decode_cookie(encoded, self.bob)

        self.assertTrue(not agent.is_trusted)

    def test_inactivity_config(self):
        with self.assertRaises(ImproperlyConfigured):
            with settings(AGENT_INACTIVITY_DAYS=()):
                self.middleware._max_cookie_age(self.agentsettings)

    def test_inactivity_precedence(self):
        self.agentsettings.inactivity_days = 30

        self.assertEqual(self.middleware._max_cookie_age(self.agentsettings), 30 * 86400)

    def _roundtrip(self, *args, **kwargs):
        agent = Agent(self.alice, *args, **kwargs)

        return self._roundtrip_agent(agent)

    def _roundtrip_agent(self, agent):
        return self._decode_cookie(self._encode_cookie(agent))

    def _encode_cookie(self, agent):
        return self.middleware._encode_cookie(agent, self.alice)

    def _decode_cookie(self, encoded):
        return self.middleware._decode_cookie(encoded, self.alice)


class DecoratorTest(AgentTrustTestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'alice')
            AgentSettings.objects.create(user=self.alice)
        except IntegrityError:
            self.skipTest("Unable to create a test user.")

        self.factory = RequestFactory()

    def test_view_1_untrusted(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.agent = Agent.untrusted_agent(self.alice)

        response = decorated_view_1(request)

        self.assertEqual(response.status_code, 302)

    def test_view_1_trusted(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.agent = Agent.trusted_agent(self.alice)

        response = decorated_view_1(request)

        self.assertEqual(response.status_code, 200)

    def test_view_2_untrusted(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.agent = Agent.untrusted_agent(self.alice)

        response = decorated_view_2(request)

        self.assertEqual(response.status_code, 302)

    def test_view_2_trusted(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.agent = Agent.trusted_agent(self.alice)

        response = decorated_view_2(request)

        self.assertEqual(response.status_code, 200)


@trusted_agent_required
def decorated_view_1(request):
    return HttpResponse()


@trusted_agent_required()
def decorated_view_2(request):
    return HttpResponse()


class HttpTestCase(AgentTrustTestCase):
    """
    Tests that exercise the full request/response cycle. These are less
    precise, but touch more code.
    """
    urls = 'django_agent_trust.test.urls'

    def setUp(self):
        try:
            user = self.create_user('alice', 'alice')
            AgentSettings.objects.create(user=user)
            self.create_user('bob', 'bob')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            self.alice = AgentClient('alice')
            self.bob = AgentClient('bob')

    def test_anonymous(self):
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_anon_trust(self):
        self.alice.trust()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_authenticated(self):
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_trusted(self):
        self.alice.login()
        self.alice.trust()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 200)

    def test_anon(self):
        self.alice.trust()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_revoked(self):
        self.alice.login()
        self.alice.trust()
        self.alice.revoke()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_exotic_username(self):
        user = self.create_user('charlie@example.com', 'charlie')
        AgentSettings.objects.create(user=user)
        charlie = AgentClient('charlie@example.com', 'charlie')

        charlie.login()
        charlie.trust()
        response = charlie.get_restricted()

        self.assertEqual(response.status_code, 200)

    def test_persist(self):
        self.alice.login()
        self.alice.trust()
        self.alice.logout()
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 200)

    def test_trusted_session(self):
        self.alice.login()
        self.alice.trust_session()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 200)

    def test_old_session(self):
        self.alice.login()
        self.alice.trust_session()
        self.alice.logout()
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_anon_session(self):
        self.alice.trust_session()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_replace_trust(self):
        self.alice.login()
        self.alice.trust()
        self.alice.trust_session()
        self.alice.logout()
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_other_trusted(self):
        self.alice.login()
        self.alice.trust()
        self.alice.logout()

        self.bob.login()
        response = self.bob.get_restricted()

        self.assertEqual(response.status_code, 302)

    def test_other_revoked(self):
        self.alice.login()
        self.alice.trust()

        self.bob.login()
        self.bob.trust()
        self.bob.revoke()
        self.bob.logout()

        response = self.alice.get_restricted()

        self.assertEqual(response.status_code, 200)

    def test_revoke_others(self):
        alice1 = AgentClient('alice')
        alice2 = AgentClient('alice')

        alice1.login()
        alice1.trust()

        alice2.login()
        alice2.trust()
        alice2.revoke_others()

        response = alice1.get_restricted()

        self.assertEqual(response.status_code, 302)


class AgentClient(Client):
    def __init__(self, username, password=None):
        super(AgentClient, self).__init__()

        self.username = username
        self.password = password if (password is not None) else username

    def login(self):
        return self.post('/login/', {'username': self.username, 'password': self.password})

    def logout(self):
        return self.post('/logout/')

    def get_restricted(self):
        return self.get('/restricted/')

    def trust(self):
        return self.post('/trust/')

    def trust_session(self):
        return self.post('/session/')

    def revoke(self):
        return self.post('/revoke/')

    def revoke_others(self):
        return self.post('/revoke_others/')
