import traceback

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View
from simple_history.utils import bulk_update_with_history

from app.delivery.models.delivery import Delivery
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class UpdDelivCompletionView(PermissionRequiredMixin, View):
    permission_required = ('delivery.edit_delivery')
    allowed_domains = settings.ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self,
            request: WSGIRequest,
            folio: str | int,
            value: str,
            *args,
            **kwargs):
        user = request.user
        error = ''
        cancel_status = False
        try:
            delivery = Delivery.objects.get(folio=folio)
        except Delivery.DoesNotExist:
            e_msg = 'No existe entrega que pueda ser cancelada'
            error = CustomError(msg=e_msg)
        except Delivery.MultipleObjectsReturned:
            e_msg = 'No existe entrega definida'
            error = CustomError(msg=e_msg)

        if not error:
            try:
                delivery.is_complete = value == 'yes'
                delivery.changed_by = user
                bulk_update_with_history(objs=[delivery],
                                         model=Delivery,
                                         fields=['is_complete', 'changed_by'])
                cancel_status = True
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nFolio: {folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {folio}'
                error = CustomError(msg=e_msg, log=tb)

        return JsonResponse(data={'status': cancel_status,
                                  'error': str(error)})
