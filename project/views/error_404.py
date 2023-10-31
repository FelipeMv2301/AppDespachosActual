from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def error_404(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
    return render(request=request,
                  context={'page_title': 'Error 404'},
                  template_name='404.html')
