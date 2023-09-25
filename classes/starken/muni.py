import json
from typing import Any, Dict, List

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.delivery.models.account import Account
from app.general.models.muni_starken import MuniStarken
from classes.starken.starken import Starken
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class Municipality(Starken):
    def __init__(self,
                 account: Account = None,
                 code: int = None,
                 name: str = None,
                 code_dls: int = None,
                 picking: bool = False,
                 agencies: List[object] = None,
                 *args,
                 **kwargs):
        super().__init__(account=account, *args, **kwargs)

        self.code = code
        self.name = name
        self.code_dls = code_dls
        self.picking = picking
        self.agencies = agencies

    @loggable
    def add_agency(self, agency: object, *args, **kwargs):
        self.agencies.append(agency)

    @loggable
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        response = requests.get(url=self.muni_api_path,
                                headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        model = MuniStarken
        munis = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        objs = {obj.code: obj
                for obj in model.objects.all()}
        for muni in munis:
            code = str(muni['code_dls'])
            name = muni['name']

            sync_kwargs = {'model': model}
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
                obj = model()

            obj.code = code
            obj.name = name
            obj.changed_by = user_obj
            sync_kwargs['objs'] = [obj]
            sync_func(**sync_kwargs)
