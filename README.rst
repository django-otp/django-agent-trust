.. image:: https://img.shields.io/pypi/v/django-agent-trust?color=blue
   :target: https://pypi.org/project/django-agent-trust/
   :alt: PyPI
.. image:: https://img.shields.io/readthedocs/django-agent-trust-official
   :target: https://django-agent-trust-official.readthedocs.io/
   :alt: Documentation
.. image:: https://img.shields.io/badge/github-django--agent--trust-green
   :target: https://github.com/django-otp/django-agent-trust
   :alt: Source

This project has tools for managing trusted user agents. For example, you might
allow the user to indicate whether they are using a public or private computer
and implement different policies for each. Or you might be using a two-factor
authentication scheme, allowing the users to bypass the second factor on
machines that they designate as trusted. This uses Django's signed cookie
facility and operates independently of sessions.

Short list of features:

    - ``request.agent.is_trusted`` tells you whether the request came from a
      trusted agent.
    - APIs to trust or revoke the agent that made a given request.
    - Global, per-user, and per-agent settings can set the duration of agent
      trust as well as an inactivity timeout.
    - Supports session-scoped agent trust for consistency of authorization
      policies.
    - Revoke all of a user's previously trusted agents at any time.

The mechanisms by which a user is allowed to designate trusted agents is left
entirely to clients of this library. For an application of this API using
one-time passwords, see `django-otp-agents
<https://pypi.org/project/django-otp-agents>`_, part of the `django-otp
<https://pypi.org/project/django-otp>`_ suite.
