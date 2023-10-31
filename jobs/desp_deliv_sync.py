from module.general.models.service_account import ServiceAccount
from classes.despachos.despachos import SERV_CODE
from classes.despachos.delivery import Delivery

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Delivery(account=serv_acct).app_sync()
