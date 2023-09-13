import json
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.general.models.muni_sap import MuniSap
from classes.sap.sap import Sap
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class MunicipalityAndCity(Sap):
    def __init__(self,
                 muni_name: str = None,
                 city_name: str = None,
                 region_code: str = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.muni_name = muni_name
        self.city_name = city_name
        self.region_code = region_code

    @loggable
    @Sap.session_handling
    def search_with_region(self, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.muni_and_city_mdl
        region_mdl = self.region_mdl

        url = self.host
        url += f'$crossjoin({region_mdl},{mdl})?'
        url += f'$expand={region_mdl}($select=Code, Name),'
        url += f'{mdl}($select=Code, Name)&'
        url += f'$filter={region_mdl}/Code eq '
        url += f'{mdl}/U_NX_Region and '
        url += f'{region_mdl}/Country eq \'{self.country_code}\''

        self.change_max_page_size(qty=700)
        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']

    @loggable
    @Sap.session_handling
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.muni_and_city_mdl

        url = self.host
        url += f'{mdl}?$select=Code, Name'

        self.change_max_page_size(qty=700)
        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']

    @loggable
    def app_sync(self, *args, **kwargs):
        model = MuniSap
        munis = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        objs = {obj.code: obj
                for obj in model.objects.all()}
        for muni in munis:
            code = str(muni['Code'])
            name = muni['Name']

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
