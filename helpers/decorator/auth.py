from typing import Callable

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect


def authentication(f: Callable):
    def wrapper(*args, **kwargs):
        request = next(a for a in args if isinstance(a, WSGIRequest))
        if not request.user.is_authenticated:
            return redirect(to='login')
        else:
            return f(*args, **kwargs)
    return wrapper
