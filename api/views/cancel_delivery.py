import traceback

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic.base import View
from simple_history.utils import bulk_update_with_history

from module.delivery.models.delivery import Delivery
from module.delivery.models.status import Status
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError
from project.settings.base import ALLOWED_PRIVATE_HOSTS


class CancelDeliveryView(PermissionRequiredMixin, View):
    permission_required = ('delivery.cancel_delivery')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, folio: str | int, *args, **kwargs):
        user = request.user
        error = ''
        cancel_status = False
        try:
            delivery = Delivery.objects.get(folio=folio,
                                            orderdelivery__order_grouping__delivery_option__carrier__code__in=['BQ', 'TD'],
                                            status__code__in=['ISSUED', 'NOTISSUED'])
        except Delivery.DoesNotExist:
            e_msg = 'No existe entrega que pueda ser cancelada'
            error = CustomError(msg=e_msg)
        except Delivery.MultipleObjectsReturned:
            e_msg = 'No existe entrega definida'
            error = CustomError(msg=e_msg)

        if not error:
            try:
                delivery.status = Status.objects.get(code='CANCEL')
                delivery.locked = True
                delivery.changed_by = user
                bulk_update_with_history(objs=[delivery],
                                         model=Delivery,
                                         fields=['status',
                                                 'locked',
                                                 'changed_by'])
                cancel_status = True
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nFolio: {folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {folio}'
                error = CustomError(msg=e_msg, log=tb)

        return JsonResponse(data={'status': cancel_status,
                                  'error': str(error)})
