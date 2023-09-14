import os
from pathlib import Path

from core.settings.base import BASE_DIR

CURRENT_PATH = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR

OUTPUT_FOLDER_PATH = os.path.join(PROJECT_DIR, 'output')
if not os.path.exists(path=OUTPUT_FOLDER_PATH):
    os.mkdir(path=OUTPUT_FOLDER_PATH)

# Web app styles data
INPUT_CLASS = 'textfield'

# Sync data
SYNC_DAYS = -30
