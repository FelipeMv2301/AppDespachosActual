import traceback

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View

from app.delivery.models.delivery import Delivery
from config.settings.base import ALLOWED_PRIVATE_HOSTS
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError
from notification.email.order import OrderEmail


class SendDelivEmailView(PermissionRequiredMixin, View):
    permission_required = ('delivery.send_delivery_email')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self,
            request: WSGIRequest,
            folio: str | int,
            email_addr: str,
            *args,
            **kwargs):
        delivery = Delivery.objects.filter(folio=folio)
        error = ''
        send_status = False
        if not delivery:
            e_msg = 'No existe entrega'
            error = CustomError(msg=e_msg)
        elif delivery.count() > 1:
            e_msg = 'No existe entrega definida'
            error = CustomError(msg=e_msg)

        if not error:
            try:
                email = OrderEmail(delivery=delivery.first(), cc=[email_addr])
                email.send_email()
                send_status = True
            except CustomError as e:
                error = e
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nFolio: {folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {folio}'
                error = CustomError(msg=e_msg, log=tb)

        return JsonResponse(data={'status': send_status, 'error': str(error)})
