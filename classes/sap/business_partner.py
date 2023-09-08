import inspect
import json
import time
from typing import List

import requests

from classes.sap.sap import Sap
from helpers.decorator.loggable import loggable


class BusinessPartner(Sap):
    def __init__(self,
                 code: str = None,
                 fullname: str = None,
                 tax_id: str = None,
                 phone_nums: List[str] = None,
                 mobi_phone_num: str = None,
                 email_addrs: str = None,
                 contacts: List[object] = None,
                 addresses: List[object] = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.fullname = fullname
        self.tax_id = tax_id
        self.phone_nums = phone_nums
        self.mobi_phone_num = mobi_phone_num
        self.email_addrs = email_addrs
        self.contacts = contacts
        self.addresses = addresses

    @loggable
    def add_contact(self, contact: object, *args, **kwargs):
        self.contacts.append(contact)

    @loggable
    def add_address(self, address: object, *args, **kwargs):
        self.addresses.append(address)
