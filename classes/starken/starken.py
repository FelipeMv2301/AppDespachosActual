import json
import traceback
from typing import Callable

import requests

from app.delivery.models.account import Account
from core.settings.base import env
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError


class Starken:
    def __init__(self, account: Account = None, *args, **kwargs):
        # Starken info for app models
        self.carrier_code = 'STK'

        # Starken account info
        self.account = (account
                        if account
                        else
                        Account.objects.filter(carrier__code=self.carrier_code).first())

        # Starken API data
        self.api_host = env.str(var='STARKEN_API_HOST')
        api_key = self.account.get_api_key()
        self.api_headers = {'apikey': api_key}
        self.agency_api_path = f'{self.api_host}agencias-externo/agency'
        self.muni_api_path = f'{self.api_host}agencias-externo/comuna'
        self.trk_api_path = f'{self.api_host}tracking-externo/orden-flete/of/{{folio}}'

        # Starken web services data
        self.ws_url = env.str(var='STARKEN_WS_URL')
        self.ws_rut = self.account.rut
        ws_rut_split = self.ws_rut.split('-')
        self.ws_rut_wo_verifier = ws_rut_split[0]
        self.ws_rut_verifier = ws_rut_split[-1]
        self.ws_user = self.account.username
        self.ws_pwd = self.account.get_password()
        self.ws_acct = self.account.number
        ws_acct_split = self.ws_acct.split('-')
        self.ws_acct_wo_verifier = ws_acct_split[-1]
        self.ws_acct_verifier = ws_acct_split[-1]
        self.ws_cost_center = self.account.cost_center

        # Starken custom errors
        self.bad_request_error = 'Bad request to Starken'

    @staticmethod
    def portal_session_handling(f: Callable):
        def wrapper(_self, *args, **kwargs):
            try:
                _self.portal_login()
                result = f(_self, *args, **kwargs)

                return result

            except Exception:
                tb = traceback.format_exc()
                e = CustomError(log=tb)
                raise e

        return wrapper

    @loggable
    def check_response(self, response: requests.Response, *args, **kwargs):
        if response.ok:
            return
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
    def portal_login(self, *args, **kwargs) -> requests.Response:
        data = {
            'user': self.portal_user,
            'pass': self.portal_pass
        }
        response = requests.post(url=self.portal_url,
                                 headers=self.portal_headers,
                                 data=data)
        # TODO: check response

        self.portal_cookies = dict(response.cookies)

        return response
