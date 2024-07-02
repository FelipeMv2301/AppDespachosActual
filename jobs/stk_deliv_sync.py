from datetime import datetime, timedelta

from module.general.models.service_account import ServiceAccount
from classes.starken.delivery import Delivery
from classes.starken.starken import Starken

sync_date = ((datetime.now() + timedelta(days=-20))
             .strftime('%Y-%m-%d'))
serv_accts = ServiceAccount.objects.filter(service__code=Starken.serv_code,
                                           enabled=True)
for serv_acct in serv_accts:
    Delivery(account=serv_acct).app_sync(from_date=sync_date)
