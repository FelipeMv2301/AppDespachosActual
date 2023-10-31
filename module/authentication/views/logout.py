from django.contrib.auth import logout
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View

from module.general.models.user_session import UserSession
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS


class Logout(View):
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        session = UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key,
            end_time__isnull=True
        ).first()
        if session:
            session.end_time = timezone.now()
            session.save()

        logout(request=request)

        return redirect(to='login')
