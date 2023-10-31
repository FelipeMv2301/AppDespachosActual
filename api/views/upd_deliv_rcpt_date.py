import traceback
from datetime import date, datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
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


class UpdDelivRcptDateView(PermissionRequiredMixin, View):
    permission_required = ('delivery.edit_deliv_rcpt_date')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

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
        upd_status = False
        try:
            delivery = (Delivery.objects
                        .get(~Q(service_acct__service__code='STK'),
                             folio=folio,
                             status__code='ISSUED'))
        except Delivery.DoesNotExist:
            e_msg = 'No existe entrega que pueda ser modificada'
            error = CustomError(msg=e_msg)
        except Delivery.MultipleObjectsReturned:
            e_msg = 'No existe entrega definida'
            error = CustomError(msg=e_msg)

        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            e_msg = 'La fecha no es válida'
            error = CustomError(msg=e_msg)

        if value > date.today():
            e_msg = 'La fecha no puede ser mayor a hoy'
            error = CustomError(msg=e_msg)

        if not error:
            try:
                delivery.rcpt_date = value
                delivery.status = Status.objects.get(code='RCVD')
                delivery.changed_by = user
                bulk_update_with_history(objs=[delivery],
                                         model=Delivery,
                                         fields=['rcpt_date',
                                                 'status',
                                                 'changed_by'])
                upd_status = True
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nFolio: {folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {folio}'
                error = CustomError(msg=e_msg, log=tb)

        return JsonResponse(data={'status': upd_status,
                                  'error': str(error)})
