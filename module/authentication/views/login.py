import os
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views import View

from module.general.models.user_profile import UserProfile
from module.general.models.user_session import UserSession
from helpers import globals as gb
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS

CURRENT_PATH = Path(__file__).resolve().parent.parent
CURRENT_FOLDERNAME = os.path.basename(CURRENT_PATH)


class Login(View):
    template = os.path.join(CURRENT_FOLDERNAME, 'login.html')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    form = AuthenticationForm()
    form_fields = ['username', 'password']
    for field in form_fields:
        form.fields[field].widget.attrs['class'] = gb.INPUT_CLASS

    context = {'form': form}

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        return render(request=request,
                      template_name=self.template,
                      context=self.context)

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        auth = AuthenticationForm(request, data=request.POST)
        if auth.is_valid():
            user = auth.get_user()
            profile = (UserProfile.objects.select_related('initial_url')
                       .filter(user=user, initial_url__enabled=True).first())
            if profile:
                url = profile.initial_url.name
            else:
                url = 'home'
            login(request=request, user=user)
            session = request.session
            UserSession.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                session_key=session.session_key,
                session_expiration=session.get_expiry_date(),
            )
            return redirect(to=url)

        context = self.context
        messages.error(
            request=request,
            message='Usuario y/o contraseña inválido'
        )

        return render(request=request,
                      template_name=self.template,
                      context=context)
