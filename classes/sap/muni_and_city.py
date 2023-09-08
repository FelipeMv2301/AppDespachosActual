import json
from typing import Any, Dict

import requests

from classes.sap.sap import Sap
from helpers.decorator.loggable import loggable


class MunicipalityAndCity(Sap):
    def __init__(self,
                 muni_name: str = None,
                 city_name: str = None,
                 region_code: str = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.muni_name = muni_name
        self.city_name = city_name
        self.region_code = region_code

    @loggable
    @Sap.session_handling
    def search_with_region(self, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.muni_and_city_mdl
        region_mdl = self.region_mdl

        url = self.host
        url += f'$crossjoin({region_mdl},{mdl})?'
        url += f'$expand={region_mdl}($select=Code, Name),'
        url += f'{mdl}($select=Code, Name)&'
        url += f'$filter={region_mdl}/Code eq '
        url += f'{mdl}/U_NX_Region and '
        url += f'{region_mdl}/Country eq \'{self.country_code}\''

        self.change_max_page_size(qty=700)
        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']

    # @loggable
    # @Sap.session_handling
    # def app_sync(self, *args, **kwargs):
    #     municipality_codes = list()
    #     region_codes = list()
    #     munis_and_regions = self.search_with_region()
    #     for i in munis_and_regions:
    #         regions_info = i[self.regions_model]
    #         region_code = regions_info['Code']
    #         region_name = regions_info['Name']
    #         municipalities_info = i[self.municipality_city_model]
    #         municipality_code = municipalities_info['Code']
    #         municipality_name = municipalities_info['Name']
    #         region_object = RegionSap.objects.filter(code=region_code)
    #         if region_code not in region_codes:
    #             region_codes.append(region_code)
    #             if region_object.exists():
    #                 region_object.update(code=region_code, name=region_name)
    #             else:
    #                 RegionSap(code=region_code, name=region_name).save()
    #         if municipality_code not in municipality_codes:
    #             municipality_codes.append(municipality_code)
    #             municipality_object = MunicipalitySap.objects.filter(
    #                 code=municipality_code)
    #             if municipality_object.exists():
    #                 municipality_object.update(
    #                     code=municipality_code,
    #                     name=municipality_name,
    #                     region=region_object[0]
    #                 )
    #             else:
    #                 MunicipalitySap(
    #                     code=municipality_code,
    #                     name=municipality_name,
    #                     region=region_object[0]
    #                 ).save()
