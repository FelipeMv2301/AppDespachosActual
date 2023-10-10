import json
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.general.models.muni_service import MuniService
from app.general.models.service_account import ServiceAccount
from classes.starken.starken import Starken
from config.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class Municipality(Starken):
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        super().__init__(account=account, *args, **kwargs)

    @loggable
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        response = requests.get(url=self.muni_api_path,
                                headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        mdl = MuniService
        munis = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        objs = mdl.objects.filter(service_acct=self.serv_account)
        objs = {obj.code: obj for obj in objs}
        for muni in munis:
            code = str(muni['code_dls'])
            name = muni['name']

            sync_kwargs = {'model': mdl}
            if code in objs:
                obj = objs[code]
                sync_func = bulk_update_with_history
                sync_kwargs['fields'] = [
                    'code',
                    'name',
                    'changed_by'
                ]
            else:
                sync_func = bulk_create_with_history
                obj = mdl()

            obj.code = code
            obj.name = name
            obj.service_acct = self.serv_account
            obj.changed_by = user_obj
            sync_kwargs['objs'] = [obj]
            sync_func(**sync_kwargs)
