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


Managing Trust
--------------

:class:`~django_agent_trust.middleware.AgentMiddleware` installs an object on
requests that will tell you whether the requesting user agent has been marked
trusted. It will also tell you what time it was originally trusted.

Agent trust is tied to authenticated users. Each user gets a different cookie,
so multiple users can maintain separate trust settings on your site using the
same machine/browser. Anonymous users always have untrusted agents.

.. autoclass:: django_agent_trust.models.Agent

You can update the status of the current agent with the following APIs:

.. automodule:: django_agent_trust
    :members: trust_current_agent, revoke_current_agent, revoke_other_agents


Limiting Access
---------------

.. automodule:: django_agent_trust.decorators
    :members:


Expiration
----------

django-agent-trust supports two types of trust expiration: simple expiration
based on the original trust date and expiration from inactivity. Both types can
be managed globally and on a per-user basis. If an expiration is set both
globally and for the current user, then the more restrictive setting takes
precedence.  All expiration settings are measured in days, although fractional
days are permitted.

Global configuration takes the form of two settings: :setting:`AGENT_TRUST_DAYS`
and :setting:`AGENT_INACTIVITY_DAYS`. Per-user configuration is done through a
model object:

.. autoclass:: django_agent_trust.models.AgentSettings
    :members:


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
Django installation or be parent of that path.


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
