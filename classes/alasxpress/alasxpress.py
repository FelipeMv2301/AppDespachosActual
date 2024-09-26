import json

import requests

from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError
from module.general.models.service_account import ServiceAccount
from project.settings.base import env


class Alasxpress:
    serv_code = 'ALAS'

    # Track
    # track_url = env.str(var='')

    def __init__(self, account: ServiceAccount, *args, **kwargs):
        # Alasxpress service account info
        self.serv_account = account
        self.acct_rut = self.serv_account.rut
        self.acct_user = self.serv_account.username

        # Alasxpress API data
        self.api_url = env.str(var='ALAS_API_URL')
        api_key = self.serv_account.get_api_key()
        self.api_headers = {'x-alas-ce0-api-key': api_key,
                            'Content-Type': 'application/json'}
        self.delivery_emission_endpoint = f'{self.api_url}delivery-orders'
        self.track_endpoint = f'{self.api_url}delivery-orders/{{folio}}'

        # Alasxpress custom errors
        self.bad_request_error = 'Bad request to Alasxpress'

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
