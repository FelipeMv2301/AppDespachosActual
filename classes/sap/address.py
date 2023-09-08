import inspect
import json
import time
from typing import List

import requests

from classes.sap.sap import Sap
from helpers.decorator.loggable import loggable


class Address(Sap):
    def __init__(self,
                 code: str = None,
                 alias_name1: str = None,
                 alias_name2: str = None,
                 address: str = None,
                 municipality: str = None,
                 city: str = None,
                 region: str = None,
                 country: str = None,
                 bsns_partner: object = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.alias_name1 = alias_name1
        self.alias_name2 = alias_name2
        self.address = address
        self.municipality = municipality
        self.city = city
        self.region = region
        self.country = country
        self.bsns_partner = bsns_partner

        self.join_bsns_partner()

    @loggable
    def join_bsns_partner(self, *args, **kwargs):
        if self.bsns_partner:
            self.bsns_partner.add_contact(contact=self)

    # @loggable
    # def search_with_contact_info(self,
    #                              contact_id: int,
    #                              *args,
    #                              **kwargs) -> dict:
    #     url = self.host
    #     url += f'$crossjoin({bp_model}, {contacts_bp_model})?'
    #     bp_model = self.model
    #     contacts_bp_model = self.contacts_bp_model
    #     url_method = (
    #         f"$crossjoin({bp_model}, {contacts_bp_model})?"
    #         f"$expand={contacts_bp_model}($select=E_Mail, MobilePhone, "
    #         "FirstName, MiddleName, LastName)"
    #         f"&$filter={bp_model}/CardCode eq "
    #         f"{contacts_bp_model}/CardCode "
    #         f"and {contacts_bp_model}/InternalCode eq {contact_id}"
    #     )
    #     url = self.sap_host + url_method
    #     headers = self.ws_headers

    #     response = requests.get(url=url, headers=headers)

    #     return json.loads(response.text)
