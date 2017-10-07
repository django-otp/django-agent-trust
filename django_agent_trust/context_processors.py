from __future__ import absolute_import, division, print_function, unicode_literals


def agent(request):
    """
    A context processor that sets the template context variable ``agent`` to
    the value of ``request.agent``.
    """
    return {'agent': getattr(request, 'agent', None)}
