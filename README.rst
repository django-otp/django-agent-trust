.. image:: https://img.shields.io/pypi/v/django-agent-trust?color=blue
   :target: https://pypi.org/project/django-agent-trust/
   :alt: PyPI
.. image:: https://img.shields.io/readthedocs/django-agent-trust-official
   :target: https://django-agent-trust-official.readthedocs.io/
   :alt: Documentation
.. image:: https://img.shields.io/badge/github-django--agent--trust-green
   :target: https://github.com/django-otp/django-agent-trust
   :alt: Source
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black


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

.. end-of-doc-intro


Development
-----------

This project is built and managed with `hatch`_. If you don't have hatch, I
recommend installing it with `pipx`_: ``pipx install hatch``.

``pyproject.toml`` defines several useful scripts for development and testing.
The default environment includes all dev and test dependencies for quickly
running tests. The ``test`` environment defines the test matrix for running the
full validation suite. Everything is executed in the context of the Django
project in test/test\_project.

As a quick primer, hatch scripts can be run with ``hatch run [<env>:]<script>``.
To run linters and tests in the default environment, just run
``hatch run check``. This should run tests with your default Python version and
the latest Django. Other scripts include:

* **manage**: Run a management command via the test project. This can be used to
  generate migrations.
* **lint**: Run all linters.
* **fix**: Run tools that can automatically fix many linting errors.
* **test**: Run all tests.
* **check**: Run linters and tests.
* **warn**: Run tests with all warnings enabled. This is especially useful for
  seeing deprecation warnings in new versions of Django.
* **cov**: Run tests and print a code coverage report.

To run the full test matrix, run ``hatch run test:run``. You will need multiple
specific Python versions installed for this.

You can clean up the hatch environments with ``hatch env prune``, for example to
force dependency updates.


.. _hatch: https://hatch.pypa.io/
.. _pipx: https://pypa.github.io/pipx/
