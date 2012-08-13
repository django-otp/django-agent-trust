from datetime import datetime, timedelta

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import Client, RequestFactory

from ..conf import settings
from ..decorators import trusted_agent_required
from ..models import AgentSettings, Agent
from ..middleware import AgentMiddleware


now = lambda: datetime.now().replace(microsecond=0)


class AgentCodingTestCase(TestCase):
    """
    Tests as much of the middleware as possible without the request/response
    cycle.
    """
    fixtures = ['tests/alice.yaml']

    def setUp(self):
        self.middleware = AgentMiddleware()
        self.agentsettings = AgentSettings.objects.get()

    def test_untrusted(self):
        agent = self._roundtrip_agent(Agent.get_untrusted())

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, None)
        self.assertEqual(agent.serial, -1)

    def test_trusted(self):
        trusted_at = now()

        agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_newly_trusted(self):
        agent = self._roundtrip(is_trusted=True)

        self.assert_(agent.is_trusted)
        self.assertEqual(agent.trusted_at, now())
        self.assertEqual(agent.serial, self.agentsettings.serial)

    def test_newly_untrusted(self):
        trusted_at = now()

        agent = self._roundtrip(is_trusted=False, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_global_only(self):
        trusted_at = now() - timedelta(days=7)

        with settings(AGENT_TRUST_DAYS=5):
            agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_user_only(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 5

        agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_user_precedence(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 5

        with settings(AGENT_TRUST_DAYS=14):
            agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_global_precedence(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 14

        with settings(AGENT_TRUST_DAYS=5):
            agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_expired_neither(self):
        trusted_at = now() - timedelta(days=7)
        self.agentsettings.trust_days = 14

        with settings(AGENT_TRUST_DAYS=14):
            agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_revoked(self):
        trusted_at = now()
        self.agentsettings.serial = 2

        agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at, serial=1)

        self.assert_(not agent.is_trusted)
        self.assertEqual(agent.trusted_at, trusted_at)
        self.assertEqual(agent.serial, 1)

    def test_revoke_reauthorize(self):
        trusted_at = now()
        self.agentsettings.serial = 2

        agent = self._roundtrip(is_trusted=True, trusted_at=trusted_at - timedelta(days=1), serial=1)
        agent.is_trusted = True
        agent = self._roundtrip_agent(agent)

        self.assert_(agent.is_trusted)
        self.assertEqual(agent.trusted_at.replace(microsecond=0), trusted_at)
        self.assertEqual(agent.serial, 2)


    def _roundtrip(self, *args, **kwargs):
        agent = Agent(*args, **kwargs)

        return self._roundtrip_agent(agent)

    def _roundtrip_agent(self, agent):
        return self._decode_cookie(self._encode_cookie(agent))

    def _encode_cookie(self, agent):
        return self.middleware._encode_cookie(agent, self.agentsettings)

    def _decode_cookie(self, encoded):
        return self.middleware._decode_cookie(encoded, self.agentsettings)


class DecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_view_1_untrusted(self):
        request = self.factory.get('/')
        request.user = None
        request.agent = Agent.get_untrusted()

        response = decorated_view_1(request)

        self.assertEqual(response.status_code, 302)

    def test_view_1_trusted(self):
        request = self.factory.get('/')
        request.user = None
        request.agent = Agent(is_trusted=True, trusted_at=now(), serial=1)

        response = decorated_view_1(request)

        self.assertEqual(response.status_code, 200)

    def test_view_2_untrusted(self):
        request = self.factory.get('/')
        request.user = None
        request.agent = Agent.get_untrusted()

        response = decorated_view_2(request)

        self.assertEqual(response.status_code, 302)

    def test_view_2_trusted(self):
        request = self.factory.get('/')
        request.user = None
        request.agent = Agent(is_trusted=True, trusted_at=now(), serial=1)

        response = decorated_view_2(request)

        self.assertEqual(response.status_code, 200)


@trusted_agent_required
def decorated_view_1(request):
    return HttpResponse()

@trusted_agent_required()
def decorated_view_2(request):
    return HttpResponse()


class HttpTestCase(TestCase):
    fixtures = ['tests/alice.yaml', 'tests/bob.yaml']
    urls = 'django_agent_trust.tests.urls'

    def setUp(self):
        self.alice = AgentClient('alice')
        self.bob = AgentClient('bob')

    def test_anonymous(self):
        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 302)

    def test_authenticated(self):
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 302)

    def test_trusted(self):
        self.alice.login()
        self.alice.trust()
        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 200)

    def test_revoked(self):
        self.alice.login()
        self.alice.trust()
        self.alice.revoke()
        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 302)

    def test_persist(self):
        self.alice.login()
        self.alice.trust()
        self.alice.logout()
        self.alice.login()
        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 200)

    def test_other_trusted(self):
        self.alice.login()
        self.alice.trust()
        self.alice.logout()

        self.bob.login()
        response = self.bob.get_restricted()

        self.assertEquals(response.status_code, 302)

    def test_other_revoked(self):
        self.alice.login()
        self.alice.trust()

        self.bob.login()
        self.bob.trust()
        self.bob.revoke()
        self.bob.logout()

        response = self.alice.get_restricted()

        self.assertEquals(response.status_code, 200)

    def test_revoke_others(self):
        alice1 = AgentClient('alice')
        alice2 = AgentClient('alice')

        alice1.login()
        alice1.trust()

        alice2.login()
        alice2.trust()
        alice2.revoke_others()

        response = alice1.get_restricted()

        self.assertEquals(response.status_code, 302)


class AgentClient(Client):
    def __init__(self, username):
        super(AgentClient, self).__init__()

        self.username = username

    def login(self):
        return self.post('/login/', {'username': self.username, 'password': self.username})

    def logout(self):
        return self.post('/logout/')

    def get_restricted(self):
        return self.get('/restricted/')

    def trust(self):
        return self.post('/trust/')

    def revoke(self):
        return self.post('/revoke/')

    def revoke_others(self):
        return self.post('/revoke_others/')
