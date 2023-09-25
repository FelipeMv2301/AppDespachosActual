from datetime import datetime, timedelta

from classes.mitocondria.delivery import Delivery
from helpers.globals import SYNC_DAYS

sync_date = ((datetime.now() + timedelta(days=SYNC_DAYS))
             .strftime('%Y-%m-%d'))
Delivery().app_sync(from_date=sync_date)
