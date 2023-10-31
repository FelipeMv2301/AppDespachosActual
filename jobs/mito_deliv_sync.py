from datetime import datetime, timedelta

from module.general.models.service_account import ServiceAccount
from classes.mitocondria.delivery import Delivery
from classes.mitocondria.mitocondria import SERV_CODE
from helpers.globals import SYNC_DAYS

sync_date = ((datetime.now() + timedelta(days=SYNC_DAYS))
             .strftime('%Y-%m-%d'))
serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Delivery(account=serv_acct).app_sync(from_date=sync_date)
