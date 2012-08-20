django-agent-trust
==================

.. include:: ../../README


Installation
------------

django-agent-trust requires at least Python 2.6 and Django 1.4. It also depends
on :mod:`django.contrib.auth`.


    #. Add ``'django_agent_trust'`` to :setting:`INSTALLED_APPS`.
    #. Add ``'django_agent_trust.middleware.AgentMiddleware'`` to
       :setting:`MIDDLEWARE_CLASSES`. It must come after
       :class:`~django.contrib.auth.middleware.AuthenticationMiddleware`.
    #. If you want to access agent information in templates, add
       ``'django_agent_trust.context_processors.agent'`` to
       :setting:`TEMPLATE_CONTEXT_PROCESSORS`.


Assessing Trust
---------------

A view can determine whether it's being requested from a trusted agent by
checking ``request.agent.is_trusted``. Agent trust is tied to authenticated
users; each user gets a different cookie, so multiple users can maintain
separate trust settings on your site using the same machine/browser. Anonymous
users always have untrusted agents.

:class:`~django_agent_trust.middleware.AgentMiddleware` installs an object on
requests that will tell you whether the requesting user agent has been marked
trusted and at what time:

.. autoclass:: django_agent_trust.models.Agent
    :members: is_trusted, is_session, trusted_at, trust_expiration

You may optionally install an included context processor to propagate these
objects to template contexts:

.. automodule:: django_agent_trust.context_processors
    :members:


Managing Trust
--------------

Agent trust may be persistent or scoped to a session. Of course, the point of
the library is the former, but the latter is included to enable more consistent
authorization polices. For example, if you ask the user whether they are on a
public or shared device, you might set session-scoped trust for public agents
and persistent trust for private agents. Your authorization policy can then
refer solely to agent trust: for public agents, this will be synonymous with
authentication; for private agents, trust will persist across login sessions.
Persistent trust is typically implemented with two-factor authentication, where
the second factor is used to establish the trusted agent.

You can update the status of the current agent with the following APIs:

.. automodule:: django_agent_trust
    :members: trust_agent, trust_session, revoke_agent, revoke_other_agents


Limiting Access
---------------

.. automodule:: django_agent_trust.decorators
    :members:


Expiration
----------

django-agent-trust supports two types of trust expiration: simple expiration
based on the original trust date and expiration from inactivity. Simple
expiration can be managed on three levels: a global setting, a per-user setting,
and a setting on the agent itself. Inactivity timeouts can be managed globally
and per-user. If any time expirations are specified at multiple levels, the most
restrictive takes precedence. All expiration settings are measured in days,
although fractional days are permitted.

Global configuration takes the form of two settings: :setting:`AGENT_TRUST_DAYS`
and :setting:`AGENT_INACTIVITY_DAYS`. Per-user configuration is done through a
model object:

.. autoclass:: django_agent_trust.models.AgentSettings
    :members:

A custom duration can be set on an individual agent at the time that it is
trusted by :func:`~django_agent_trust.trust_agent`.

Settings
--------

.. setting:: AGENT_COOKIE_DOMAIN

**AGENT_COOKIE_DOMAIN**

Default: ``None``

The domain to use for agent cookies or ``None`` to use a standard domain.


.. setting:: AGENT_COOKIE_HTTPONLY

**AGENT_COOKIE_HTTPONLY**

Default: ``True``

Whether to use HTTPOnly flag on agent cookies. If this is set to True,
client-side JavaScript will not to be able to access the session cookie in many
browsers.


.. setting:: AGENT_COOKIE_NAME

**AGENT_COOKIE_NAME**

Default: ``'agent-trust'``

A prefix for agent cookies. This can be anything.


.. setting:: AGENT_COOKIE_PATH

**AGENT_COOKIE_PATH**

Default: ``'/'``

The path set on the agent cookies. This should either match the URL path of your
Django installation or be a parent of that path.


.. setting:: AGENT_COOKIE_SECURE

**AGENT_COOKIE_SECURE**

Default: ``False``

Whether to use a secure cookie for the agent cookies. If this is set to
``True``, the cookie will be marked as "secure," which means browsers may ensure
that the cookie is only sent under an HTTPS connection.


.. setting:: AGENT_LOGIN_URL 

**AGENT_LOGIN_URL**

Default: :setting:`LOGIN_URL`

The URL where requests are redirected for login when using the
:func:`~django_agent_trust.decorators.trusted_agent_required` decorator.


.. setting:: AGENT_TRUST_DAYS 

**AGENT_TRUST_DAYS**

Default: ``None``

The number of days an agent will remain trusted. This can be ``None`` to impose
no limit.


.. setting:: AGENT_INACTIVITY_DAYS 

**AGENT_INACTIVITY_DAYS** 

Default: ``365``

The number of days allowed between requests before an agent's trust is revoked.
This can not be ``None`` (all cookies expire eventually), but you can always set
it to a very large number.


Changes
-------

:doc:`changes`


License
-------

.. include:: ../../LICENSE
