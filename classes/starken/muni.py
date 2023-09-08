import json
# from app.order.models.agency_starken import AgencyStarken as StkAg
# from app.order.models.municipality_starken import \
#     MunicipalityStarken as StkMuni
from typing import Any, Dict, List

import requests

from classes.starken.starken import Starken
from helpers.decorator.loggable import loggable


class Municipality(Starken):
    def __init__(self,
                 code: int = None,
                 name: str = None,
                 code_dls: int = None,
                 picking: bool = False,
                 agencies: List[object] = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.name = name
        self.code_dls = code_dls
        self.picking = picking

    @loggable
    def add_agency(self, agency: object, *args, **kwargs):
        self.agencies.append(agency)

    @loggable
    def search_all(self, *args, **kwargs) -> Dict[str, Any]:
        response = requests.get(url=self.muni_api_path,
                                headers=self.api_headers)
        # TODO: check response before return

        return json.loads(s=response.text)

    # @loggable
    # def app_sync(self, *args, **kwargs) -> None:
    #     '''also synchronizes the agencies'''
    #     municipalities = self.get()
    #     for m in municipalities:
    #         stk_muni_id = m['id']
    #         code_dls = m['code_dls']
    #         name = m['name']
    #         pickup_enabled = m['retiro_habilitado']
    #         agencies = m['agencies']
    #         municipality_object_search = StkMuni.objects.filter(
    #             stk_id=stk_muni_id)
    #         if municipality_object_search.exists():
    #             municipality_object_search.update(
    #                 code_dls=code_dls,
    #                 name=name,
    #                 pickup_enabled=pickup_enabled
    #             )
    #             municipality_object = municipality_object_search[0]
    #         else:
    #             municipality_object_creation = StkMuni.objects.create(
    #                 stk_id=stk_muni_id,
    #                 code_dls=code_dls,
    #                 name=name,
    #                 pickup_enabled=pickup_enabled
    #             )
    #             municipality_object_creation.save()
    #             municipality_object = StkMuni.objects.filter(
    #                 id=municipality_object_creation.id)[0]

    #         for a in agencies:
    #             stk_ag_id = a['id']
    #             name = a['name']
    #             code_dls = a['code_dls']
    #             if code_dls is None:
    #                 continue
    #             address = a['address']
    #             latitude = a['latitude']
    #             longitude = a['longitude']
    #             shipping = a['shipping']
    #             delivery = a['delivery']
    #             status = a['status']
    #             agency_object_search = StkAg.objects.filter(
    #                 stk_id=stk_ag_id)
    #             if agency_object_search.exists():
    #                 agency_object_search.update(
    #                     code_dls=code_dls,
    #                     name=name,
    #                     address=address,
    #                     latitude=latitude,
    #                     longitude=longitude,
    #                     shipping=shipping,
    #                     delivery=delivery,
    #                     status=status,
    #                     stk_municipality=municipality_object
    #                 )
    #             else:
    #                 StkAg(
    #                     stk_id=stk_ag_id,
    #                     code_dls=code_dls,
    #                     name=name,
    #                     address=address,
    #                     latitude=latitude,
    #                     longitude=longitude,
    #                     shipping=shipping,
    #                     delivery=delivery,
    #                     status=status,
    #                     stk_municipality=municipality_object
    #                 ).save()
