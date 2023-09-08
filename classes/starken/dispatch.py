import json
import os
from datetime import datetime

import pandas as pd
import requests
import wget
# from app.dispatch.models.dispatch import Dispatch as DispApp
from django.contrib.auth.models import User
from django.core.signing import Signer
from simple_history.utils import bulk_update_with_history
from zeep import Client

from classes.starken.starken import Starken
# from classes.starken.models.starken_account import StarkenAccount
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable

# from helpers.notification.classes.error_card import ErrorCard


class Dispatch(Starken):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @loggable
    @Starken.portal_session_handling
    def export_portal_report(self, from_date: str = None, *args, **kwargs):
        today = datetime.now().strftime('%Y-%m-%d')
        data = {
            'fecha_emi_ini': from_date or today,
            'fecha_emi_fin': today,
            'fecha_compro_ini': '-1',
            'fecha_compro_fin': '-1',
            'fecha_ent_ini': '-1',
            'fecha_ent_fin': '-1',
            'swDctos': '0',
            't_ent': '-1',
            't_pago': '-1',
            't_servicio': '-1',
            'bultos': '0',
            'kgs': '0',
            'origins': '-1',
            'destinations': '-1',
            'estados': '-1',
            'ctas': '-1',
        }
        response = requests.post(url=self.report_url,
                                 headers=self.portal_headers,
                                 data=data,
                                 cookies=self.portal_cookies)
        # TODO: check response before return
        report_download_url = json.loads(s=response.text)['url']

        wget.download(url=report_download_url, out=self.report_output_path)

    # @loggable
    # def app_sync(self, *args, **kwargs) -> None:
    #     app_user = User.objects.get(username=APP_USERNAME)

    #     self.export_portal_report()
    #     report = pd.read_csv(filepath_or_buffer=self.report_output_path,
    #                          sep=';',
    #                          encoding='utf-8',
    #                          encoding_errors='ignore')
    #     report_rows_number = report.index.stop
    #     report_json = json.loads(report.to_json())
    #     freight_folios = report_json['orden']
    #     delivery_dates = report_json['fecha_entrega']
    #     states = report_json['estado']
    #     except_descs = report_json['ult_excep']
    #     report = [{
    #         'folio': freight_folios[str(i)],
    #         'delivery_date': (delivery_dates[str(i)]
    #                           if delivery_dates[str(i)] != ''
    #                           else
    #                           None),
    #         'status': states[str(i)].capitalize(),
    #         'except_descs': (except_descs[str(i)]
    #                          if except_descs[str(i)] != ''
    #                          else
    #                          None)
    #     } for i in range(report_rows_number)]

    #     for r in report:
    #         folio = r['folio']
    #         delivery_date = r['delivery_date']
    #         status = r['status']
    #         except_desc = r['except_descs']
    #         object_search = DispApp.objects.filter(folio=folio)
    #         if object_search.exists():
    #             objs = object_search
    #             for obj in objs:
    #                 obj.reception_date = delivery_date
    #                 obj.status = status
    #                 obj.exception_description = except_desc
    #                 obj.changed_by = app_user
    #                 bulk_update_with_history(
    #                     objs,
    #                     DispApp,
    #                     [
    #                         'reception_date',
    #                         'status',
    #                         'exception_description',
    #                         'changed_by'
    #                     ]
    #                 )
    #         else:
    #             ErrorCard(content_card=[
    #                 {
    #                     'buttom_label': 'error',
    #                     'content': 'Folio Starken inexistente en BDD'
    #                 },
    #                 {
    #                     'buttom_label': 'folio',
    #                     'content': folio
    #                 }
    #             ]).send_card()

    #     os.remove(path=self.report_output_path)

    # @loggable
    # def folio_emission(self,
    #                    account: StarkenAccount,
    #                    client_name: str,
    #                    dispatch_address: str,
    #                    dispatch_municipality: str,
    #                    client_phone_number: str,
    #                    client_email: str,
    #                    contact_name: str,
    #                    shipping_type: str,
    #                    shipping_pay_type: str,
    #                    dispatch_value: str,
    #                    height: str,
    #                    width: str,
    #                    length: str,
    #                    weight: str,
    #                    docs: list,
    #                    packages_qty: str,
    #                    observations: str,
    #                    *args,
    #                    **kwargs) -> dict:
    #     signer = Signer()

    #     ws_client = Client(wsdl=self.ws_url)
    #     body = {
    #         'rutEmpresaEmisora': account.rut,
    #         'rutUsuarioEmisor': account.username,
    #         'claveUsuarioEmisor': signer.unsign_object(account.password),
    #         'rutDestinatario': '?',
    #         'dvRutDestinatario': '?',
    #         'nombreRazonSocialDestinatario': client_name,
    #         'apellidoPaternoDestinatario': '.',
    #         'apellidoMaternoDestinatario': '.',
    #         'direccionDestinatario': dispatch_address,
    #         'numeracionDireccionDestinatario': '.',
    #         'departamentoDireccionDestinatario': '?',
    #         'comunaDestino': dispatch_municipality,
    #         'telefonoDestinatario': client_phone_number,
    #         'emailDestinatario': client_email,
    #         'nombreContactoDestinatario': contact_name,
    #         'tipoEntrega': shipping_type,
    #         'tipoPago': shipping_pay_type,
    #         'numeroCtaCte': account.account_number,
    #         'dvNumeroCtaCte': account.account_verifier_digit,
    #         'centroCostoCtaCte': account.cost_center,
    #         'valorDeclarado': dispatch_value,
    #         'contenido': 'Material Educativo',
    #         'kilosTotal': weight,
    #         'alto': height,
    #         'ancho': width,
    #         'largo': length,
    #         'tipoServicio': '0',
    #         'tipoDocumento1': '',
    #         'numeroDocumento1': '',
    #         'generaEtiquetaDocumento1': '',
    #         'tipoDocumento2': '?',
    #         'numeroDocumento2': '?',
    #         'generaEtiquetaDocumento2': '?',
    #         'tipoDocumento3': '?',
    #         'numeroDocumento3': '?',
    #         'generaEtiquetaDocumento3': '?',
    #         'tipoDocumento4': '?',
    #         'numeroDocumento4': '?',
    #         'generaEtiquetaDocumento4': '?',
    #         'tipoDocumento5': '?',
    #         'numeroDocumento5': '?',
    #         'generaEtiquetaDocumento5': '?',
    #         'tipoEncargo1': '29',
    #         'cantidadEncargo1': packages_qty,
    #         'tipoEncargo2': '?',
    #         'cantidadEncargo2': '?',
    #         'tipoEncargo3': '?',
    #         'cantidadEncargo3': '?',
    #         'tipoEncargo4': '?',
    #         'cantidadEncargo4': '?',
    #         'tipoEncargo5': '?',
    #         'cantidadEncargo5': '?',
    #         'ciudadOrigenNom': 'Santiago',
    #         'observacion': str(observations),
    #         'codAgenciaOrigen': '?',
    #     }

    #     for i in range(len(docs)):
    #         index = i + 1
    #         doc_info = docs[i]
    #         body[f'tipoDocumento{index}'] = str(doc_info['stk_code'])
    #         body[f'numeroDocumento{index}'] = str(doc_info['doc_folio'])
    #         body[f'generaEtiquetaDocumento{index}'] = 'S'

    #     response = ws_client.service.Execute(body)

    #     return response
