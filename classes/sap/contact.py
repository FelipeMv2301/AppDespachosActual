import json
from typing import Any, Dict

import requests

from module.general.models.service_account import ServiceAccount
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
        url += f'$crossjoin({bp_mdl}, {mdl})?'
        url += f'$expand={mdl}($select=E_Mail, MobilePhone, '
        url += 'FirstName, MiddleName, LastName, Name, Phone1, Phone2, '
        url += f'Address)&$filter={mdl}/CardCode eq {bp_mdl}/CardCode '
        url += f'and {mdl}/InternalCode eq {contact_id}'

        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']
