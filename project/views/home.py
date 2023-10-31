from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable


@authentication
@loggable
def home(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
    return render(request=request, template_name='main.html')
