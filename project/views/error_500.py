from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def error_500(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
    return render(request=request,
                  context={'page_title': 'Error 500'},
                  template_name='500.html')
