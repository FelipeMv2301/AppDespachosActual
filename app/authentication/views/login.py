import os
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views import View

from helpers import globals as gb
from helpers.decorator.loggable import loggable

CURRENT_PATH = Path(__file__).resolve().parent.parent
CURRENT_FOLDERNAME = os.path.basename(CURRENT_PATH)


class Login(View):
    template = os.path.join(CURRENT_FOLDERNAME, 'login.html')

    form = AuthenticationForm()
    form_fields = ['username', 'password']
    for field in form_fields:
        form.fields[field].widget.attrs['class'] = gb.INPUT_CLASS

    context = {'form': form}

    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        return render(request=request,
                      template_name=self.template,
                      context=self.context)

    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        auth = AuthenticationForm(request, data=request.POST)
        if auth.is_valid():
            login(request=request, user=auth.get_user())
            return redirect(to='home')

        context = self.context
        messages.error(
            request=request,
            message='Usuario y/o contraseña inválido'
        )

        return render(request=request,
                      template_name=self.template,
                      context=context)
