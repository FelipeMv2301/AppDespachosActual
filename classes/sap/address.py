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
