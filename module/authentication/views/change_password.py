import os
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views import View

from helpers import globals as gb
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS

CURRENT_PATH = Path(__file__).resolve().parent.parent
CURRENT_FOLDERNAME = os.path.basename(CURRENT_PATH)


class ChangePassword(View):
    template = os.path.join(CURRENT_FOLDERNAME, 'change_password.html')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @staticmethod
    def form(request: WSGIRequest, *args, **kwargs):
        form_args = [request.user]
        if request.method == 'POST':
            form_args.append(request.POST)
        form = PasswordChangeForm(*form_args)
        form_fields = [
            'old_password',
            'new_password1',
            'new_password2'
        ]
        for field in form_fields:
            form.fields[field].widget.attrs['class'] = gb.INPUT_CLASS

        return form

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        context = {'form': self.form(request=request)}

        return render(
            request=request,
            template_name=self.template,
            context=context
        )

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        form = self.form(request=request)
        context = {'form': form}
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request=request, user=user)
            messages.success(
                request=request,
                message='Contraseña modificada correctamente'
            )
        else:
            messages.error(
                request=request,
                message='La contraseña no pudo ser modificada'
            )

        return render(request=request,
                      template_name=self.template,
                      context=context)
