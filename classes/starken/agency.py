import json
from typing import Any, Dict

import requests

from classes.starken.starken import Starken
from helpers.decorator.loggable import loggable


class Agency(Starken):
    def __init__(self,
                 code: int = None,
                 name: str = None,
                 code_dls: int = None,
                 address: str = None,
                 shipping: bool = False,
                 delivery: bool = False,
                 phone_num: str = None,
                 muni: object = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.name = name
        self.code_dls = code_dls
        self.address = address
        self.shipping = shipping
        self.delivery = delivery
        self.phone_num = phone_num
        self.muni = muni

        self.join_municipality()

    @loggable
    def join_municipality(self, *args, **kwargs):
        if self.muni:
            self.muni.add_agency(agency=self)

    @loggable
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        response = requests.get(url=self.agency_api_path,
                                headers=self.api_headers)
        # TODO: check response before return

        return json.loads(s=response.text)
