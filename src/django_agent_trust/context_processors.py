def agent(request):
    """
    A context processor that sets the template context variable ``agent`` to
    the value of ``request.agent``.
    """
    return {'agent': getattr(request, 'agent', None)}
