v1.1.0 - February 08, 2024 - Tools and packaging
--------------------------------------------------------------------------------

This project is now managed with `hatch`_, which replaces setuptools, pipenv,
and tox. Users of the package should not be impacted. Developers can refer to
the readme for details. If you're packaging this project from source, I suggest
relying on pip's isolated builds rather than using hatch directly.

- Fix `#12_`: We no longer create `AgentSettings` objects when loading
  fixtures.


.. _hatch: https://hatch.pypa.io/
.. _#12: https://github.com/django-otp/django-agent-trust/issues/12


v1.0.4 - November 29, 2021 - Forward compatibility
--------------------------------------------------------------------------------

Default to AutoField to avoid spurious migrations.



v1.0.3 - August 01, 2021 - Cookie management
-------------------------------------------------------------------------------

- Fix `#9`_: We now delete cookies for untrusted agents rather than saving
  them. :class:`~django_agent_trust.middleware.AgentMiddleware` also now
  includes a subclass hook for implementing more complex cookie policies.


.. _#9: https://github.com/django-otp/django-agent-trust/issues/9


v1.0.2 - February 12, 2021 - AgentSettings improvement
-------------------------------------------------------------------------------

- Fix `#6`_: Trap and ignore the inevitable get_or_create race condition on
  AgentSettings. This also adds a signal handler to automatically initialize
  AgentSettings for new users, which should avoid this race condition in the
  first place.


.. _#6: https://github.com/django-otp/django-agent-trust/issues/6


v1.0.1 - September 21, 2020 - AgentSettings improvement
-------------------------------------------------------------------------------

- Fix `#2`_: Improved AgentSettings initialization.


.. _#2: https://github.com/django-otp/django-agent-trust/issues/2


v1.0.0 - August 13, 2020 - Drop unsupported Python and Django versions
-------------------------------------------------------------------------------

- Now supports Python>=3.5 and Django>=2.2.


v0.4.1 - September 12, 2019 - Preliminary Django 3.0 support
------------------------------------------------------------

Removed dependencies on Python 2 compatibility shims in Django < 3.0.


v0.4.0 - August 26, 2019 - Housekeeping
---------------------------------------

Routine updates to version dependencies and test matrix, plus miscellaneous
cleanup.


v0.3.1 - December 4, 2017 - Django 2.0
--------------------------------------

- Add support for Django 2.0.


v0.3.0 - October 7, 2017 - Forward compatibility
------------------------------------------------

- Drop support for obsolete versions of Python and Django.

- Various cleanup and reorganization for forward compatibility.


v0.2.2 - September 4, 2016 - Django 1.10
----------------------------------------

- Adds support for the new middleware API in Django 1.10.


v0.2.1 - July 7, 2015 - South migration
---------------------------------------

- Adds an initial migration for Django < 1.7 with South.

.. warning::

    If you're using South, you'll need to run ``manage.py migrate --fake
    django_agent_trust 0001`` after upgrading.


v0.2.0 - May 22, 2015 - Djano migration
---------------------------------------

- Adds an initial migration for Django >=1.7.

.. warning::

    If you're using Django >=1.8, you'll need to run ``manage.py migrate
    --fake-initial django_agent_trust`` after upgrading.


v0.1.9 - April 3, 2015 - Django 1.8 compatibility
-------------------------------------------------

- Fixes testing issues and deprecation warnings on Django 1.8.


v0.1.8 - September 9, 2013 - Python 3 compatibility
---------------------------------------------------

- Tests pass with Django 1.6 under python 3.2 and 3.3.

- Added a tox.ini for automated testing in multiple environments.


v0.1.7 - August 19, 2013 - Fix for usernames with symbols
---------------------------------------------------------

- Cookie names now incorporate a hash of the username rather than the username
  itself.

.. warning::

    Updating to this version will effectively revoke all previously trusted
    agents.


v0.1.6 - May 9, 2013 - Django 1.5 compatibility
-----------------------------------------------

Custom user models are now supported.

Unit tests have been updated to work across Django versions, with and without
USE_TZ=True.


v0.1.5 - October 8, 2012 - Django < 1.4
---------------------------------------

The middleware is now disabled in Django < 1.4 and all unit tests are skipped.


v0.1.4 - Sep 10, 2012 - Admin cosmetics
---------------------------------------

- Add :func:`AgentSettings.unicode
  <django_agent_trust.models.AgentSettings.unicode>` for the benefit of the
  admin site.


v0.1.3 - Aug 20, 2012 - Packaging fix
-------------------------------------

- Switch to setuptools to install fixtures. The tests will fail otherwise.


v0.1.2 - Aug 19, 2012 - Security fix
------------------------------------

- Include the username in the signed cookie payload and don't accept it for any
  other user.


v0.1.1 - Aug 19, 2012 - Minor improvements
------------------------------------------

- Added :func:`django_agent_trust.context_processors.agent`.

- Added :attr:`Agent.is_session <django_agent_trust.models.Agent.is_session>` to
  indicate session-scoped trusted agents.


v0.1.0 - Aug 13, 2012 - Initial release
---------------------------------------

Initial beta release. This project was spun off of `django-otp-agents
<http://pypi.python.org/pypi/django-otp-agents>`_, part of the `django-otp
<http://pypi.python.org/pypi/django-otp>`_ suite.
