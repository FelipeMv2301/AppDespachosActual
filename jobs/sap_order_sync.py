from datetime import datetime, timedelta

from classes.sap.order import Order
from helpers.globals import SYNC_DAYS

sync_date = ((datetime.now() + timedelta(days=SYNC_DAYS))
             .strftime('%Y-%m-%d'))
Order().app_sync(from_date=sync_date)
