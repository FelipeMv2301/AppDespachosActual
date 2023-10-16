from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View

from helpers.decorator.domain import domain_check


class CheckAuthView(View):
    allowed_domains = settings.ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    def get(self, request: WSGIRequest, *args, **kwargs):
        return JsonResponse(
            data={'authenticated': request.user.is_authenticated}
        )
