import json
import traceback
from typing import Callable

import requests

from core.settings.base import env
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError


class Sap:
    def __init__(self, *args, **kwargs):
        # SAP's service layer data
        self.host = env.str(var='SAP_HOST')
        self.max_page_size_var = 'odata.maxpagesize={qty}'
        self.headers = {
            'Prefer': self.max_page_size_var.format(qty=20)
        }
        self.logged_in = False

        # SAP's service layer models
        self.order_mdl = 'Orders'
        self.order_addrs_mdl = f'{self.order_mdl}/AddressExtension'
        self.bsns_partner_mdl = 'BusinessPartners'
        self.bsns_partner_contact_mdl = f'{self.bsns_partner_mdl}/ContactEmployees'
        self.muni_and_city_mdl = 'U_NX_COMYCIU'
        self.region_mdl = 'States'
        self.dispatch_mdl = 'DeliveryNotes'
        self.dispatch_lines_mdl = f'{self.dispatch_mdl}/DocumentLines'
        self.sales_person_mdl = 'SalesPersons'

        # SAP's fixed vars
        self.country_code = 'CL'

        # SAP custom errors
        self.bad_request_error = 'Bad request to SAP'
        self.no_sap_login = 'Cannot login to SAP service layer'
        self.no_sap_logout = 'Cannot logout to SAP service layer'

    @staticmethod
    def session_handling(f: Callable):
        def wrapper(_self, *args, **kwargs):
            try:
                _self.login()
                result = f(_self, *args, **kwargs)
                _self.logout()

                return result

            except Exception:
                tb = traceback.format_exc()
                e = CustomError(log=tb)
                raise e

        return wrapper

    @loggable
    def change_max_page_size(self, qty: int, *args, **kwargs):
        self.headers['Prefer'] = self.max_page_size_var.format(qty=qty)

    @loggable
    def check_response(self, response: requests.Response, *args, **kwargs):
        if not response.ok or 'error' in response.text:
            request = response.request
            log_data = {
                'request': {
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(requests.utils.default_headers()
                                    if request.headers is None
                                    else
                                    request.headers),
                    'body': str(request.body),
                },
                'response': {
                    'value': response.text,
                    'headers': dict(requests.utils.default_headers()
                                    if response.headers is None
                                    else
                                    response.headers),
                    'status': response.status_code,
                    'cookies': dict({}
                                    if response.cookies is None
                                    else
                                    response.cookies),
                }
            }
            log_data = json.dumps(obj=log_data)
            e = CustomError(msg=self.bad_request_error, log=log_data)
            raise e

    @loggable
    def login(self, *args, **kwargs) -> requests.Response:
        url = f'{self.host}Login'
        payload = json.dumps({
            'CompanyDB': env.str(var='SAP_DATABASE'),
            'UserName': env.str(var='SAP_USER'),
            'Password': env.str(var='SAP_PASS')
        })

        session_id_key = 'SessionId'
        session_cookie = 'B1SESSION={session_id}; ROUTEID=.node1'
        attempt = 1
        while not self.logged_in:
            response = requests.post(url=url, data=payload)
            if response.ok:
                try:
                    resp_content = json.loads(response.text)
                except json.decoder.JSONDecodeError:
                    pass
                self.logged_in = session_id_key in resp_content
            if self.logged_in:
                session_id = resp_content.get(session_id_key)
                self.headers = {
                    'Cookie': session_cookie.format(session_id=session_id)
                }

                return response
            else:
                if attempt >= 5:
                    e = CustomError(msg=self.no_sap_login)
                    raise e
                attempt += 1

    @loggable
    def logout(self, *args, **kwargs) -> requests.Response:
        url = f'{self.host}Logout'

        attempt = 1
        while not self.logged_in:
            response = requests.get(url=url)
            if response.ok:
                self.logged_in = False

                return response
            else:
                if attempt >= 5:
                    e = CustomError(msg=self.no_sap_logout)
                    raise e
                attempt += 1
