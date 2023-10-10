import json

import requests

from app.general.models.service_account import ServiceAccount
from core.settings.base import env
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError

SERV_CODE = 'STK'


class Starken:
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        # Starken service account info
        self.serv_code = SERV_CODE
        self.serv_account = account

        # Starken API data
        self.api_host = env.str(var='STARKEN_API_HOST')
        api_key = self.serv_account.get_api_key()
        self.api_headers = {'apikey': api_key}
        self.branch_api_path = f'{self.api_host}agencias-externo/agency'
        self.muni_api_path = f'{self.api_host}agencias-externo/comuna'
        self.trk_api_path = f'{self.api_host}tracking-externo/orden-flete/of/{{folio}}'

        # Starken web services data
        self.ws_url = env.str(var='STARKEN_WS_URL')
        self.ws_rut = self.serv_account.rut
        ws_rut_split = self.ws_rut.split('-')
        self.ws_rut_wo_verifier = ws_rut_split[0]
        self.ws_rut_verifier = ws_rut_split[-1]
        self.ws_user = self.serv_account.username
        self.ws_pwd = self.serv_account.get_password()
        self.ws_acct = self.serv_account.number
        ws_acct_split = self.ws_acct.split('-')
        self.ws_acct_wo_verifier = ws_acct_split[0]
        self.ws_acct_verifier = ws_acct_split[-1]
        self.ws_cost_center = self.serv_account.cost_center

        # Starken custom errors
        self.bad_request_error = 'Bad request to Starken'

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
