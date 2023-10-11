from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View


class CheckAuthView(View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        return JsonResponse(
            data={'authenticated': request.user.is_authenticated}
        )
