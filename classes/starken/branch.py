import json
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from module.delivery.models.branch import Branch as BranchMdl
from app.general.models.address import Address
from app.general.models.muni import Muni
from app.general.models.muni_service import MuniService
from app.general.models.service_account import ServiceAccount
from classes.google_maps.gmaps import GoogleMaps
from classes.starken.starken import Starken
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError
from project.settings.base import APP_USERNAME


class Branch(Starken):
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        super().__init__(account=account, *args, **kwargs)

    @loggable
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        response = requests.get(url=self.branch_api_path,
                                headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        mdl = BranchMdl
        addr_mdl = Address
        serv_muni_mdl = MuniService
        muni_mdl = Muni
        branches = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)
        gmaps = GoogleMaps()

        munis = {}
        branch_objs = mdl.objects.filter(service_acct=self.serv_account)
        branch_objs = {obj.code: obj for obj in branch_objs}
        branch_obj_cods = list(branch_objs.keys())
        for branch in branches:
            code = str(branch['code_dls'])
            name = branch['name']
            phone = branch['phone']
            shipping = branch['shipping']
            delivery = branch['delivery']
            address = branch['address']
            latitude = float(branch['latitude'])
            longitude = float(branch['longitude'])
            status = branch['status']
            enabled = status == 'ACTIVE'
            muni = branch['comuna']
            muni_code = muni['code_dls']

            if muni_code not in munis:
                stk_muni_obj = (serv_muni_mdl.objects
                                .filter(code=muni_code,
                                        service_acct=self.serv_account))
                if not stk_muni_obj:
                    e_msg = f'Starken muni code {muni_code} does not exist'
                    CustomError(msg=e_msg, notify=True)
                    continue
                stk_muni_obj = stk_muni_obj.first()
                muni_obj = stk_muni_obj.muni
                if not muni_obj:
                    muni_name_from_gmaps = gmaps.get_muni_by_latlng(
                        lat=latitude, lng=longitude)
                    try:
                        muni_obj = muni_mdl.objects.get(
                            name=muni_name_from_gmaps)
                    except muni_mdl.DoesNotExist:
                        e_msg = f'Starken muni code {muni_code} '
                        e_msg += 'has no equivalence'
                        CustomError(msg=e_msg, notify=True)
                        continue
                munis[muni_code] = muni_obj
            muni_obj = munis[muni_code]

            addr_sync_kwargs = {'model': addr_mdl}
            sync_kwargs = {'model': mdl}
            if code in branch_objs:
                branch_obj = branch_objs[code]
                addr_obj = branch_obj.addr
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
                branch_obj = mdl()
                addr_obj = addr_mdl()

            addr_obj.st_and_num = address
            addr_obj.muni = muni_obj
            addr_obj.latitude = latitude
            addr_obj.longitude = longitude
            addr_obj.changed_by = user_obj
            addr_sync_kwargs['objs'] = [addr_obj]
            addr_sync = sync_func(**addr_sync_kwargs)
            addr_obj = addr_sync[0] if addr_sync else addr_obj

            branch_obj.code = code
            branch_obj.name = name
            branch_obj.addr = addr_obj
            branch_obj.phone = phone
            branch_obj.service_acct = self.serv_account
            branch_obj.shipping = shipping
            branch_obj.delivery = delivery
            branch_obj.enabled = enabled
            branch_obj.changed_by = user_obj
            sync_kwargs['objs'] = [branch_obj]
            sync_func(**sync_kwargs)

            if code in branch_obj_cods:
                branch_obj_cods.remove(code)

        unsync_ags = [branch_objs[code] for code in branch_obj_cods]
        for branch in unsync_ags:
            branch.enabled = False
            branch.changed_by = user_obj
        bulk_update_with_history(
            objs=unsync_ags,
            model=mdl,
            fields=['enabled', 'changed_by']
        )
