from datetime import datetime, timedelta

from app.general.models.service_account import ServiceAccount
from classes.sap.order import Order
from classes.sap.sap import SERV_CODE
from helpers.globals import SYNC_DAYS

sync_date = ((datetime.now() + timedelta(days=SYNC_DAYS))
             .strftime('%Y-%m-%d'))
serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Order(account=serv_acct).app_sync(from_date=sync_date)
