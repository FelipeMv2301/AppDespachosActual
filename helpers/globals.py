import os
import pathlib

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()

# Web app styles data
INPUT_CLASS = 'textfield'

# Sync data
SYNC_DAYS = -30

# Maps
MAPS_FOLDER_PATH = os.path.join(CURRENT_PATH, 'map')
CL_REGIONS_GEOJSON_PATH = os.path.join(MAPS_FOLDER_PATH, 'geojson_chile.json')
