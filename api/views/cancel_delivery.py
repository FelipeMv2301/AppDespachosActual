from django.core.handlers.wsgi import WSGIRequest
from django.views.generic.base import View
from simple_history.utils import bulk_update_with_history

from app.delivery.models.delivery import Delivery
from app.delivery.models.status import Status
from helpers.error.custom_error import CustomError


class CancelDeliveryView(View):
    def get(self, request: WSGIRequest, folio: str | int, *args, **kwargs):
        user = request.user
        try:
            delivery = (
                Delivery.objects
                .get(folio=folio,
                     orderdelivery__order_grouping__delivery_option__carrier__code__in=['BQ', 'TD'])
            )
        except Delivery.DoesNotExist:
            e_msg = 'No existe entrega'
            e = CustomError(msg=e_msg)
            raise e
        except Delivery.MultipleObjectsReturned:
            e_msg = 'No existe entrega definida'
            e = CustomError(msg=e_msg)
            raise e

        delivery.status = Status.objects.get(code='CANCEL')
        delivery.locked = True
        delivery.changed_by = user
        bulk_update_with_history(objs=[delivery],
                                 model=Delivery,
                                 fields=['status', 'locked', 'changed_by'])

        return True
