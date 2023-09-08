import inspect
import json
import time
from typing import Any, Dict, List

import requests

from classes.sap.sap import Sap
from helpers.decorator.loggable import loggable


class Contact(Sap):
    def __init__(self,
                 code: str = None,
                 first_name: str = None,
                 middle_name: str = None,
                 last_name: str = None,
                 address: str = None,
                 phone_nums: List[str] = None,
                 mobi_phone_num: str = None,
                 email_addrs: str = None,
                 bsns_partner: object = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.address = address
        self.phone_nums = phone_nums
        self.mobi_phone_num = mobi_phone_num
        self.email_addrs = email_addrs
        self.bsns_partner = bsns_partner

        self.join_bsns_partner()

    @loggable
    def join_bsns_partner(self, *args, **kwargs):
        if self.bsns_partner:
            self.bsns_partner.add_contact(contact=self)

    @loggable
    @Sap.session_handling
    def search_by_id(self, contact_id: int, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.bsns_partner_contact_mdl
        bp_mdl = self.bsns_partner

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
