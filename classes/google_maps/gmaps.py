import traceback

import googlemaps

from core.settings.base import env
from helpers.error.custom_error import CustomError


class GoogleMaps:
    def __init__(self, *args, **kwargs):
        api_key = env(var='GMAPS_API_KEY')
        self.gmaps = googlemaps.Client(key=api_key)

    def get_muni_by_latlng(self,
                           lat: float,
                           lng: float,
                           *args,
                           **kwargs) -> str | None:
        muni = None
        try:
            addrs = self.gmaps.reverse_geocode((lat, lng))
            addrs_comps = addrs[0]['address_components']
            for comp in addrs_comps:
                types = comp['types']
                if 'administrative_area_level_3' in types:
                    muni = comp['long_name']
                    break
        except Exception:
            tb = traceback.format_exc()
            e_msg = 'Error: municipality could not be found'
            CustomError(msg=e_msg, log=tb)

        return muni
