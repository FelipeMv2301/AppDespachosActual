import json
import traceback
from typing import Any, Dict

import pandas as pd
import requests
from django.contrib.auth.models import User
from django.db.models import CharField, F, Max, Value
from django.db.models.functions import Concat
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)
from zeep import Client

from app.delivery.models.account import Account
from app.delivery.models.delivery import Delivery as DelivMdl
from app.delivery.models.status import Status
from app.delivery.models.status_carrier import StatusCarrier
from app.order.models.delivery import OrderDelivery
from classes.starken.starken import Starken
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class Delivery(Starken):
    def __init__(self,
                 account: Account = None,
                 folio: int = None,
                 *args,
                 **kwargs):
        super().__init__(account=account, *args, **kwargs)

        self.folio = folio

    @loggable
    def track_by_folio(self, *args, **kwargs) -> Dict[str, Any]:
        url = self.trk_api_path.format(folio=self.folio)
        response = requests.get(url=url, headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        mdl = DelivMdl
        status_mdl = StatusCarrier
        user_obj = User.objects.get(username=APP_USERNAME)
        carrier = self.account.carrier

        delivs = mdl.objects.filter(account=self.account)
        status = {st.code: st
                  for st in status_mdl.objects.filter(carrier=carrier)}
        for deliv in delivs:
            self.folio = deliv.folio
            try:
                tracking = self.track_by_folio()
            except CustomError:
                print(f'Folio: {self.folio}')
                continue
            except Exception:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'{UNEXP_ERROR}\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue

            try:
                status_id = str(tracking['status_id'])
                status_desc = tracking['status_op']
                update_date = (pd.to_datetime(arg=tracking['updated_at'])
                               .to_pydatetime())

            except KeyError:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue
            try:
                status_obj = status[status_id]
                status_name = status_obj.name
                if status_desc != status_name:
                    status_obj.name = status_desc
                    status_obj.changed_by = user_obj
                    try:
                        bulk_update_with_history(objs=[status_obj],
                                                 model=status_mdl,
                                                 fields=['name', 'changed_by'])
                    except Exception:
                        tb = traceback.format_exc()
                        tb += f'Folio: {self.folio}'
                        e_msg = f'Error: {UNEXP_ERROR}'
                        e_msg += f'\nFolio: {self.folio}'
                        CustomError(msg=e_msg, log=tb)
                        continue
            except KeyError:
                status_obj = status_mdl(
                    code=status_id,
                    name=status_desc,
                    carrier=carrier,
                    changed_by=user_obj
                )
                try:
                    status_obj = bulk_create_with_history(objs=[status_obj],
                                                          model=status_mdl)[0]
                except Exception:
                    tb = traceback.format_exc()
                    tb += f'Folio: {self.folio}'
                    e_msg = f'Error: {UNEXP_ERROR}'
                    e_msg += f'\nFolio: {self.folio}'
                    CustomError(msg=e_msg, log=tb)
                    continue
                status[status_id] = status_obj

            fields_to_upd = ['carrier_status', 'changed_by']
            if status_obj.status:
                deliv.status = status_obj.status
                fields_to_upd.append('status')
                if status_obj.status.code == Status.receiv_code:
                    deliv.rcpt_date = update_date
                    fields_to_upd.append('rcpt_date')
            deliv.carrier_status = status_desc
            deliv.changed_by = user_obj
            try:
                bulk_update_with_history(objs=[deliv],
                                         model=mdl,
                                         fields=fields_to_upd)
            except Exception:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue

    @loggable
    def issue(self, delivery: DelivMdl, *args, **kwargs):
        deliv = (OrderDelivery.objects
                 .filter(delivery__id=delivery.id)
                 .values(
                     cust_name=F('order_grouping__customer__name'),
                     addr=Concat('order_grouping__addr__st_and_num',
                                 Value(' '),
                                 'order_grouping__addr__complement',
                                 output_field=CharField()),
                     muni_code=F('order_grouping__addr__muni__code'),
                     cntct_phone_num=F('order_grouping__contact__mobile_phone'),
                     cntct_email_addr=F('order_grouping__contact__email_addr'),
                     cntct_name=Concat('order_grouping__contact__first_name',
                                       Value(' '),
                                       'order_grouping__contact__last_name',
                                       output_field=CharField()),
                 )
                 .annotate(
                     max_id=Max('delivery__id'),
                     dummy_field=Value('', output_field=CharField())
                 )
                 .filter(delivery__id=F('max_id')))
        deliv = deliv[0]

        ws_client = Client(wsdl=self.ws_url)
        body = {
            'rutEmpresaEmisora': self.ws_rut_wo_verifier,
            'rutUsuarioEmisor': self.ws_user,
            'claveUsuarioEmisor': self.ws_pwd,
            'rutDestinatario': '?',
            'dvRutDestinatario': '?',
            'nombreRazonSocialDestinatario': deliv['cust_name'],
            'apellidoPaternoDestinatario': '.',
            'apellidoMaternoDestinatario': '.',
            'direccionDestinatario': deliv['addr'],
            'numeracionDireccionDestinatario': '.',
            'departamentoDireccionDestinatario': '?',
            'comunaDestino': deliv['muni_code'],
            'telefonoDestinatario': deliv['cntct_phone_num'],
            'emailDestinatario': deliv['cntct_email_addr'],
            'nombreContactoDestinatario': deliv['cntct_name'],
            'tipoEntrega': shipping_type,
            'tipoPago': shipping_pay_type,
            'numeroCtaCte': self.ws_acct_wo_verifier,
            'dvNumeroCtaCte': self.ws_acct_verifier,
            'centroCostoCtaCte': self.ws_cost_center,
            'valorDeclarado': dispatch_value,
            'contenido': 'Material Educativo',
            'kilosTotal': weight,
            'alto': height,
            'ancho': width,
            'largo': length,
            'tipoServicio': '0',
            'tipoDocumento1': '',
            'numeroDocumento1': '',
            'generaEtiquetaDocumento1': '',
            'tipoDocumento2': '?',
            'numeroDocumento2': '?',
            'generaEtiquetaDocumento2': '?',
            'tipoDocumento3': '?',
            'numeroDocumento3': '?',
            'generaEtiquetaDocumento3': '?',
            'tipoDocumento4': '?',
            'numeroDocumento4': '?',
            'generaEtiquetaDocumento4': '?',
            'tipoDocumento5': '?',
            'numeroDocumento5': '?',
            'generaEtiquetaDocumento5': '?',
            'tipoEncargo1': '29',
            'cantidadEncargo1': packages_qty,
            'tipoEncargo2': '?',
            'cantidadEncargo2': '?',
            'tipoEncargo3': '?',
            'cantidadEncargo3': '?',
            'tipoEncargo4': '?',
            'cantidadEncargo4': '?',
            'tipoEncargo5': '?',
            'cantidadEncargo5': '?',
            'ciudadOrigenNom': 'Santiago',
            'observacion': str(observations),
            'codAgenciaOrigen': '?',
        }

        for i in range(len(docs)):
            index = i + 1
            doc_info = docs[i]
            body[f'tipoDocumento{index}'] = str(doc_info['stk_code'])
            body[f'numeroDocumento{index}'] = str(doc_info['doc_folio'])
            body[f'generaEtiquetaDocumento{index}'] = 'S'

        response = ws_client.service.Execute(body)

        return response
