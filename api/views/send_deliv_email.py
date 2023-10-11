from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F
from django.views.generic.base import View

from app.delivery.models.delivery import Delivery
from helpers.error.custom_error import CustomError
from notification.email.order_shipped_email import OrderShippedEmail


class SendDelivEmailView(View):
    def get(self, request: WSGIRequest, folio: str | int, *args, **kwargs):
        delivery = Delivery.objects.filter(folio=folio)
        if not delivery:
            e_msg = 'No existe entrega'
            e = CustomError(msg=e_msg)
            raise e
        elif delivery.count() > 1:
            e_msg = 'No existe entrega definida'
            e = CustomError(msg=e_msg)
            raise e

        deliv_data = (delivery
                      .values(serv_code=F('orderdelivery__order_grouping__delivery_option__carrier__code'))
                      .first())
        if deliv_data['serv_code'] == 'STK':
            email = OrderShippedEmail(delivery=delivery.first())
            email.send_email()
            return True

        return False
