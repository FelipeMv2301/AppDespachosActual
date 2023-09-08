import traceback
from typing import Callable

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect

from core.settings.base import logger
from helpers.error.custom_error import CustomError


def loggable(f: Callable):
    def wrapper(*args, **kwargs):
        try:
            request = next(a for a in args if isinstance(a, WSGIRequest))
        except StopIteration:
            request = ''
        user = None
        if request:
            user = request.user
            logger.info(msg=f'User: {user}')
        try:
            result = f(*args, **kwargs)
            return result
        except CustomError:
            pass
        except Exception:
            tb = traceback.format_exc()
            e = CustomError(log=tb)
            if request:
                request_detail = {
                    'request': {
                        'METHOD': request.method,
                        'PATH': request.path,
                        'GET': request.GET,
                        'POST': request.POST,
                        'FILES': request.FILES,
                        'META': request.META,
                    }
                }
                logger.info(msg=request_detail)
                messages.error(request=request, message=e)
                return redirect(to='app_home')
            raise e
    return wrapper
