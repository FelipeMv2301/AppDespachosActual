from app.general.models.service_account import ServiceAccount
from classes.starken.muni import Municipality
from classes.starken.starken import SERV_CODE

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Municipality(account=serv_acct).app_sync()
