import json
from typing import Any, Dict

import requests

from app.general.models.service_account import ServiceAccount
from classes.sap.sap import Sap
from helpers.decorator.loggable import loggable


class Contact(Sap):
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        super().__init__(account=account, *args, **kwargs)

    @loggable
    @Sap.session_handling
    def search_by_id(self, contact_id: int, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.bsns_partner_contact_mdl
        bp_mdl = self.bsns_partner_mdl

        url = self.host
        url += f'$crossjoin({mdl}, {bp_mdl})?'
        url += f'$expand={bp_mdl}($select=E_Mail, MobilePhone, '
        url += 'FirstName, MiddleName, LastName)'
        url += f'&$filter={mdl}/CardCode eq '
        url += f'{bp_mdl}/CardCode '
        url += f'and {bp_mdl}/InternalCode eq {contact_id}'

        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']
