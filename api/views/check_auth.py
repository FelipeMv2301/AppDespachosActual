from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View

from helpers.decorator.domain import domain_check
from project.settings.base import ALLOWED_PRIVATE_HOSTS


class CheckAuthView(View):
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    def get(self, request: WSGIRequest, *args, **kwargs):
        return JsonResponse(
            data={'authenticated': request.user.is_authenticated}
        )
