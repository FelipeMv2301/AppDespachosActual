import json
import re
import traceback
from datetime import date
from typing import Any, Dict

import pandas as pd
import requests
from django.contrib.auth.models import User
from django.db.models import Case, CharField, F, Value, When
from django.db.models.functions import Cast, Coalesce, Concat
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)
from unidecode import unidecode

from classes.alasxpress.alasxpress import Alasxpress
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError
from module.delivery.models.delivery import Delivery as DelivMdl
from module.delivery.models.receiver import Receiver
from module.delivery.models.status import Status
from module.delivery.models.status_service import StatusService
from module.general.models.service_account import ServiceAccount
from module.order.models.delivery import OrderDelivery
from project.settings.base import APP_USERNAME


class Delivery(Alasxpress):
    def __init__(self,
                 account: ServiceAccount,
                 folio: int = None,
                 labels_url: str | str = None,
                 *args,
                 **kwargs):
        super().__init__(account=account, *args, **kwargs)

        self.folio = folio
        self.labels_url = labels_url

    @loggable
    def issue(self, delivery: DelivMdl, data: Dict, *args, **kwargs):
        """Method to issue the delivery with Alasxpress"""
        deliv = (
            OrderDelivery.objects
            .filter(delivery=delivery)
            .values(
                deliv_id=F('delivery__id'),
                customer_taxid=F('order_grouping__customer__tax_id'),
                customer_name=F('order_grouping__customer__name'),
                contact_name=Concat('order_grouping__contact__first_name',
                                    Value(' '),
                                    'order_grouping__contact__last_name',
                                    output_field=CharField()),
                email_addr=Coalesce('order_grouping__contact__email_addr',
                                    Value('')),
                mobile_phone=Coalesce('order_grouping__contact__mobile_phone',
                                      Value('')),
                addr=Coalesce('order_grouping__addr__st_and_num', Value('')),
                addr_complement=Coalesce('order_grouping__addr__complement', Value('')),
                obs=Concat(
                    Cast(F('order_grouping__addr__reference'), CharField()),
                    Value('||'),
                    Cast(F('order_grouping__addr__schedules'), CharField()),
                    Value('||'),
                    Cast(F('order_grouping__deliv_obs'), CharField()),
                    output_field=CharField()
                ),
                muni=Coalesce('order_grouping__addr__muni__name', Value('')),
            ).distinct()
        )
        if not deliv.exists():
            tb = traceback.format_exc()
            tb += f'Query: {deliv.query}'
            tb += f'\nFolio: {delivery.folio}'
            tb += f'\nId: {delivery.id}'
            e_msg = 'Error: el despacho no existe'
            e_msg += f'\nFolio: {delivery.folio}'
            e = CustomError(msg=e_msg, log=tb, notify=True)
            raise e
        deliv = deliv.first()

        phone = deliv['mobile_phone'].replace(' ', '').replace('+56', '')
        addr_ref = f'{deliv['addr_complement']} {deliv['obs']}'

        body = {
            'senderCode': self.acct_rut,
            'partner': self.acct_user,
            'receiverCode': deliv['customer_taxid'],
            'receiverFirstName': deliv['customer_name'][:50],
            'receiverLastName': '.',
            'receptorName': deliv['customer_name'][:50],
            'receiverEmail': deliv['email_addr'],
            'receiverMobilePhone': phone[:9],
            'destinationStreet': deliv['addr'][:100],
            'destinationNumber': '.',
            'destinationReference': addr_ref[:1000],
            'destinationCity': deliv['muni'][:50],
            'deliveryOrderCode': delivery.folio,
            'productsCodes': [str(i) for i in range(int(data['packg_qty']))],
            'deliveryLabelsSync': True
        }

        print(json.dumps(obj=body, indent=4))
        response = requests.post(url=self.delivery_emission_endpoint,
                                 data=json.dumps(obj=body),
                                 headers=self.api_headers)
        try:
            response_body = json.loads(s=response.text)
            if not response.ok:
                log_msg = f'\nBody: {str(body)}'
                log_msg += f'\nResponse: {str(response_body)}'
                log_msg += f'\nFolio: {delivery.folio}'
                e = CustomError(log=log_msg, notify=True)
                raise e
            else:
                self.folio = response_body['deliveryOrderId']
                self.labels_url = response_body['labelsUrl']
        except Exception:
            tb = traceback.format_exc()
            tb += f'\nBody: {body}'
            tb += f'\nResponse: {response.text}'
            tb += f'\nFolio: {delivery.folio}'
            tb += f'\nId: {delivery.id}'
            e_msg = 'Error: ha ocurrido un error insperado posterior a la '
            e_msg += 'emisión del despacho. Por favor contáctese con el '
            e_msg += 'administrador antes de volver a intentarlo'
            e_msg += f'\nFolio: {delivery.folio}'
            e = CustomError(msg=e_msg, log=tb, notify=True)
            raise e
