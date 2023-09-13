import json
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.general.models.employee_sap import EmployeeSap
from classes.sap.sap import Sap
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class SalesPerson(Sap):
    def __init__(self,
                 code: str = None,
                 name: str = None,
                 enabled: bool = True,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.name = name
        self.enabled = enabled

    @loggable
    @Sap.session_handling
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.sales_person_mdl

        url = f'{self.host}{mdl}'

        self.change_max_page_size(qty=100)
        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']

    @loggable
    def app_sync(self, *args, **kwargs):
        model = EmployeeSap
        empls = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        objs = {obj.code: obj
                for obj in model.objects.all()}
        for empl in empls:
            code = str(empl['SalesEmployeeCode'])
            name = empl['SalesEmployeeName']
            locked = empl['Locked'] == 'tNO'
            active = empl['Active'] == 'tYES'
            enabled = locked and active

            sync_kwargs = {'model': model}
            if code in objs:
                obj = objs[code]
                sync_func = bulk_update_with_history
                sync_kwargs['fields'] = [
                    'code',
                    'name',
                    'enabled',
                    'changed_by'
                ]
            else:
                sync_func = bulk_create_with_history
                obj = model()

            obj.code = code
            obj.name = name
            obj.enabled = enabled
            obj.changed_by = user_obj
            sync_kwargs['objs'] = [obj]
            sync_func(**sync_kwargs)
