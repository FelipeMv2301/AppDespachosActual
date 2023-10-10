from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render


def home(request: WSGIRequest):
    return render(
        request=request,
        template_name='main.html'
    )


def error_404(request: WSGIRequest, exception):
    """Manejo de error 404"""
    return render(
        request=request,
        template_name="404.html"
    )


def error_500(request: WSGIRequest):
    """Manejo de error 500"""
    return render(
        request=request,
        template_name="500.html"
    )


def redirect_to_rg276(request: WSGIRequest):
    rg_url = 'https://docs.google.com/spreadsheets/d/1KWKclWl7WEMrBtRlaLoCBd4wGknXB8LlHwRPfn6yvo4'
    return redirect(to=rg_url)
