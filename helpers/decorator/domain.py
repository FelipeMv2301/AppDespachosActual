from typing import Callable, List

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse


def domain_check(allowed_domains=List[str]):
    def decorator(f: Callable):
        def wrapper(*args, **kwargs):
            try:
                request = next(a for a in args if isinstance(a, WSGIRequest))
                domain = request.META.get('HTTP_HOST').split(':')[0]
                if domain not in allowed_domains:
                    response = HttpResponse()
                    response.status_code = 502
                    return response
            except StopIteration:
                pass
            return f(*args, **kwargs)
        return wrapper
    return decorator
