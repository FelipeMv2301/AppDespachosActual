import json
import traceback
from datetime import date
from typing import Any, Dict

import pandas as pd
import requests
from django.contrib.auth.models import User
from django.db.models import Case, CharField, F, TextField, Value, When
from django.db.models.functions import Coalesce, Concat
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)
from zeep import Client

from app.delivery.models.delivery import Delivery as DelivMdl
from app.delivery.models.status import Status
from app.delivery.models.status_service import StatusService
from app.general.models.service_account import ServiceAccount
from app.order.models.delivery import OrderDelivery
from classes.starken.starken import Starken
from config.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class Delivery(Starken):
    def __init__(self,
                 account: ServiceAccount,
                 folio: int = None,
                 rcpt_commit_date: date | str = None,
                 issue_date: date = None,
                 *args,
                 **kwargs):
        super().__init__(account=account, *args, **kwargs)

        self.folio = folio
        self.rcpt_commit_date = rcpt_commit_date
        self.issue_date = issue_date

    @loggable
    def track_by_folio(self, *args, **kwargs) -> Dict[str, Any]:
        url = self.trk_api_path.format(folio=self.folio)
        response = requests.get(url=url, headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, from_date: str, *args, **kwargs):
        mdl = DelivMdl
        status_mdl = StatusService
        user_obj = User.objects.get(username=APP_USERNAME)

        delivs = mdl.objects.filter(service_acct=self.serv_account,
                                    issue_date__gte=from_date)
        status = status_mdl.objects.filter(service_acct=self.serv_account)
        status = {st.code: st for st in status}
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
                CustomError(msg=e_msg, log=tb, notify=True)
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
                CustomError(msg=e_msg, log=tb, notify=True)
                continue
            try:
                status_obj = status[status_id]
            except KeyError:
                status_obj = status_mdl(
                    code=status_id,
                    name=status_desc,
                    service_acct=self.serv_account,
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
                    CustomError(msg=e_msg, log=tb, notify=True)
                    continue
                status[status_id] = status_obj

            fields_to_upd = ['service_status', 'changed_by']
            if status_obj.status:
                deliv.status = status_obj.status
                fields_to_upd.append('status')
                if status_obj.status.code == Status.receiv_code:
                    deliv.rcpt_date = update_date
                    fields_to_upd.append('rcpt_date')
            deliv.service_status = status_obj
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
                CustomError(msg=e_msg, log=tb, notify=True)
                continue

    @loggable
    def issue(self, delivery: DelivMdl, data: Dict, *args, **kwargs):
        """
        Method to issue the delivery with Starken,
        obtaining the folio identifier:

        Parameters:
        -----------
        delivery (object): Delivery model object.
        data (dict): dictionary with delivery information.

        Formats:
        --------
        data: {
            'height': 0.0,
            'width': 0.0,
            'length': 0.0,
            'weight': 0.0,
            'valuation': 0,
            'packg_qty': 0,
            'docs': [
                {
                    'type': <DocType: DocType object>,
                    'type_service': <DocType: DocTypeService object>,
                    'folio': 0
                },
                {
                    'type': <DocType: DocType object>,
                    'type_service': <DocType: DocTypeService object>,
                    'folio': 0
                }
            ]
        }

        Where:
        - 'height': (float) Total height of packages.
        - 'width': (float) Total width of packages.
        - 'length': (float) Total length of packages.
        - 'weight': (float) Total weight of packages.
        - 'packg_qty': (int) Quantity of delivery packages.
        - 'valuation': (int) Total valuation of delivery products.
        - 'docs': (list) List of tax documents related to the delivery
            of the tax documents.
        - 'type': (object) Object of the Document Type model.
        - 'folio': (int) Document folio.
        """
        deliv = (
            OrderDelivery.objects
            .filter(delivery=delivery,
                    order_grouping__delivery_option__type__typeservice__service_acct=delivery.service_acct,
                    order_grouping__delivery_option__pay_type__paytypeservice__service_acct=delivery.service_acct)
            .values(
                deliv_id=F('delivery__id'),
                customer_name=F('order_grouping__customer__name'),
                addr=Concat('order_grouping__addr__st_and_num',
                            Value(' '),
                            'order_grouping__addr__complement',
                            output_field=CharField()),
                deliv_type_code=F('order_grouping__delivery_option__type__typeservice__code'),
                deliv_pay_type_code=F('order_grouping__delivery_option__pay_type__paytypeservice__code'),
                mobile_phone=Coalesce('order_grouping__contact__mobile_phone',
                                      Value('')),
                phone1=Coalesce('order_grouping__contact__phone1', Value('')),
                phone2=Coalesce('order_grouping__contact__phone2', Value('')),
                email_addr=Coalesce('order_grouping__contact__email_addr',
                                    Value('')),
                contact_name=Concat('order_grouping__contact__first_name',
                                    Value(' '),
                                    'order_grouping__contact__last_name',
                                    output_field=CharField()),
                obs=Coalesce('order_grouping__deliv_obs', TextField('')),
                muni_value=Case(
                    When(order_grouping__delivery_option__branch__code=None,
                         then=F('order_grouping__addr__muni__muniservice__name')),
                    default=Concat(Value('@'),
                                   'order_grouping__delivery_option__branch__code',
                                   output_field=CharField()),
                )
            ).distinct()
        )
        print('deliv', deliv)
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

        try:
            height = data['height']
            width = data['width']
            length = data['length']
            weight = data['weight']
            valuation = data['valuation']
            packg_qty = data['packg_qty']
            docs = data['docs']
            docs[0]['type_service'].code
            docs[0]['folio']
        except Exception as e:
            tb = traceback.format_exc()
            tb += f'\nFolio: {delivery.folio}'
            tb += f'\nId: {delivery.id}'
            e_msg = 'Error: '
            if isinstance(e, KeyError):
                e_msg += 'información de despacho insuficiente'
            elif isinstance(e, IndexError):
                e_msg += 'no existe información de documentos de despacho'
            elif isinstance(e, AttributeError):
                e_msg += 'el tipo de documento de despacho no es el esperado'
            else:
                e_msg += UNEXP_ERROR
            e_msg += f'\nFolio: {delivery.folio}'
            e = CustomError(msg=e_msg, log=tb, notify=True)
            raise e

        phone_nums = []
        if deliv['phone1']:
            phone_nums.append(deliv['phone1'])
        if deliv['phone2']:
            phone_nums.append(deliv['phone2'])
        if deliv['mobile_phone']:
            phone_nums.append(deliv['mobile_phone'])

        # ws_client = Client(wsdl=self.ws_url)  # For WS
        body = {
            'rutEmpresaEmisora': self.acct_rut_wo_verifier,
            'rutUsuarioEmisor': self.acct_user,
            'claveUsuarioEmisor': self.acct_pwd,
            'rutDestinatario': '?',
            'dvRutDestinatario': '?',
            'nombreRazonSocialDestinatario': deliv['customer_name'],
            'apellidoPaternoDestinatario': '.',
            'apellidoMaternoDestinatario': '.',
            'direccionDestinatario': deliv['addr'],
            'numeracionDireccionDestinatario': '.',
            'departamentoDireccionDestinatario': '?',
            'comunaDestino': deliv['muni_value'],
            'telefonoDestinatario': ' '.join(phone_nums),
            'emailDestinatario': deliv['email_addr'],
            'nombreContactoDestinatario': deliv['contact_name'],
            'tipoEntrega': deliv['deliv_type_code'],
            'tipoPago': deliv['deliv_pay_type_code'],
            'numeroCtaCte': self.acct_wo_verifier,
            'dvNumeroCtaCte': self.acct_verifier,
            'centroCostoCtaCte': self.acct_cost_center,
            'valorDeclarado': valuation,
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
            'cantidadEncargo1': packg_qty,
            'tipoEncargo2': '?',
            'cantidadEncargo2': '?',
            'tipoEncargo3': '?',
            'cantidadEncargo3': '?',
            'tipoEncargo4': '?',
            'cantidadEncargo4': '?',
            'tipoEncargo5': '?',
            'cantidadEncargo5': '?',
            'ciudadOrigenNom': 'Santiago',
            'observacion': deliv['obs'],
            'codAgenciaOrigen': '?',
        }

        for i in range(len(docs)):
            index = i + 1
            doc_info = docs[i]
            body[f'tipoDocumento{index}'] = str(doc_info['type_service'].code)
            body[f'numeroDocumento{index}'] = str(doc_info['folio'])
            body[f'generaEtiquetaDocumento{index}'] = 'S'
        print('body', body)

        # response = ws_client.service.Execute(body)  # For WS
        response = requests.post(url=self.issue_api_host,
                                 data=json.dumps(obj=body),
                                 headers={'Content-Type': 'application/json'})  # For Rest
        # print('response', response)  # For WS
        print('response', response.text)  # For Rest

        try:
            response = json.loads(s=response.text)  # For Rest
            if response['codigoError'] != 0:
                e_desc = response['descripcionError']
                e_msg = f'Error: {e_desc}'
                e_msg += f'\nBody: {body}'
                e_msg += f'\nResponse: {response}'
                e_msg += f'\nFolio: {delivery.folio}'
                e = CustomError(msg=e_msg, notify=True)
                raise e
            else:
                self.folio = int(response['nroOrdenFlete'])
                self.rcpt_commit_date = response['fechaEstimadaEntrega']
                self.issue_date = response['fechaEmision']
        except KeyError:
            tb = traceback.format_exc()
            tb += f'\nBody: {body}'
            # tb += f'\nResponse: {response}'  # For WS
            tb += f'\nResponse: {response.text}'  # For Rest
            tb += f'\nFolio: {delivery.folio}'
            tb += f'\nId: {delivery.id}'
            e_msg = 'Error: ha ocurrido un error insperado posterior a la '
            e_msg += 'emisión del despacho. Por favor contáctese con el '
            e_msg += 'administrador antes de volver a intentarlo'
            e_msg += f'\nFolio: {delivery.folio}'
            e = CustomError(msg=e_msg, log=tb, notify=True)
            raise e
