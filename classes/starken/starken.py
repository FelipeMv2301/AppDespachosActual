import os
import traceback
from typing import Callable

import requests
from fake_useragent import UserAgent

from core.settings.base import env
from helpers import globals as gb
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError


class Starken:
    def __init__(self, *args, **kwargs):
        # Starken's user portal data
        self.portal_host = env.str(var='STARKEN_PORTAL_HOST')
        self.portal_url = f'{self.portal_host}webCtaCte/scripts/control.php'
        self.portal_user = env.str(var='STARKEN_PORTAL_USER')
        self.portal_pass = env.str(var='STARKEN_PORTAL_PASS')
        self.portal_cookies = {}
        self.portal_headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': UserAgent().googlechrome,
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.report_url = f'{self.portal_host}webCtaCte/panel/informes/get_informe.php'
        self.report_output_path = os.path.join(gb.OUTPUT_FOLDER_PATH,
                                               'starken.txt')

        # Starken's API data
        self.api_host = env.str(var='STARKEN_API_HOST')
        api_key = env.str(var='STARKEN_API_KEY')
        self.api_headers = {'apikey': api_key}
        self.agency_api_path = f'{self.api_host}agencias-externo/agency'
        self.muni_api_path = f'{self.api_host}agencias-externo/comuna'

        # Starken's web services data
        self.ws_url = env.str(var='STARKEN_WS_URL')

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
