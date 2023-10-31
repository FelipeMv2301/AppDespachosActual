from datetime import datetime, timedelta

from module.general.models.service_account import ServiceAccount
from classes.sap.order import Order
from classes.sap.sap import SERV_CODE
from helpers.globals import SYNC_DAYS

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)

date_fmt = '%Y-%m-%d'
today = datetime.now()
time_rage_in_days = 30
sync_start_days = SYNC_DAYS
while sync_start_days < 0:
    sync_end_days = sync_start_days + time_rage_in_days
    if sync_end_days > 0:
        sync_end_days = sync_start_days - sync_start_days
    from_sync_date = ((today + timedelta(days=sync_start_days))
                      .strftime(date_fmt))
    to_sync_date = ((today + timedelta(days=sync_end_days))
                    .strftime(date_fmt))
    for serv_acct in serv_accts:
        Order(account=serv_acct).app_sync(from_date=from_sync_date,
                                          to_date=to_sync_date)

    sync_start_days = sync_end_days
