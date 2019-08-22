from __future__ import absolute_import, division, print_function, unicode_literals


def is_anonymous(user):
    """
    Handles user.is_anonymous for all supported Django versions.
    """
    result = user.is_anonymous
    if callable(result):
        result = result()

    return result


def is_authenticated(user):
    """
    Handles user.is_authenticated for all supported Django versions.
    """
    result = user.is_authenticated
    if callable(result):
        result = result()

    return result
