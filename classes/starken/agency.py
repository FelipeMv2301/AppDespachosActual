import json
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.delivery.models.agency import Agency as AgencyMdl
from app.delivery.models.carrier import Carrier
from app.general.models.address import Address
from app.general.models.muni_starken import MuniStarken
from classes.starken.starken import Starken
from core.settings.base import APP_USERNAME
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
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        model = AgencyMdl
        addr_mdl = Address
        agencies = self.search_all()
        carrier_obj = Carrier.objects.get(name=self.carrier_name)
        user_obj = User.objects.get(username=APP_USERNAME)

        munis = {}
        ag_objs = {obj.code: obj
                   for obj in model.objects.filter(carrier=carrier_obj)}
        ag_obj_cods = list(ag_objs.keys())
        for ag in agencies:
            code = str(ag['code_dls'])
            name = ag['name']
            phone = ag['phone']
            shipping = ag['shipping']
            delivery = ag['delivery']
            address = ag['address']
            latitude = float(ag['latitude'])
            longitude = float(ag['longitude'])
            status = ag['status']
            enabled = status == 'ACTIVE'
            muni = ag['comuna']
            muni_code = muni['code_dls']

            if muni_code not in munis:
                stk_muni_obj = MuniStarken.objects.filter(code=muni_code)
                if not stk_muni_obj:
                    error_msg = f'Comuna Starken {muni_code} no encontrada'
                    continue
                stk_muni_obj = stk_muni_obj.first()
                muni_obj = stk_muni_obj.muni
                if not muni_obj:
                    error_msg = f'Comuna Starken {muni_code} sin comuna rel'
                    continue
                munis[muni_code] = muni_obj
            muni_obj = munis[muni_code]

            addr_sync_kwargs = {'model': addr_mdl}
            sync_kwargs = {'model': model}
            if code in ag_objs:
                ag_obj = ag_objs[code]
                addr_obj = ag_obj.addr
                sync_func = bulk_update_with_history
                addr_sync_kwargs['fields'] = [
                    'st_and_num',
                    'muni',
                    'latitude',
                    'longitude',
                    'changed_by'
                ]
                sync_kwargs['fields'] = [
                    'code',
                    'name',
                    'addr',
                    'phone',
                    'carrier',
                    'shipping',
                    'delivery',
                    'enabled',
                    'changed_by'
                ]
            else:
                sync_func = bulk_create_with_history
                ag_obj = model()
                addr_obj = addr_mdl()

            addr_obj.st_and_num = address
            addr_obj.muni = muni_obj
            addr_obj.latitude = latitude
            addr_obj.longitude = longitude
            addr_obj.changed_by = user_obj
            addr_sync_kwargs['objs'] = [addr_obj]
            addr_sync = sync_func(**addr_sync_kwargs)
            addr_obj = addr_sync[0] if addr_sync else addr_obj

            ag_obj.code = code
            ag_obj.name = name
            ag_obj.addr = addr_obj
            ag_obj.phone = phone
            ag_obj.carrier = carrier_obj
            ag_obj.shipping = shipping
            ag_obj.delivery = delivery
            ag_obj.enabled = enabled
            ag_obj.changed_by = user_obj
            sync_kwargs['objs'] = [ag_obj]
            sync_func(**sync_kwargs)

            if code in ag_obj_cods:
                ag_obj_cods.remove(code)

        unsync_ags = [ag_objs[code] for code in ag_obj_cods]
        for ag in unsync_ags:
            ag.enabled = False
            ag.changed_by = user_obj
        bulk_update_with_history(
            objs=unsync_ags,
            model=model,
            fields=['enabled', 'changed_by']
        )
