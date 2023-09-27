from app.general.models.service_account import ServiceAccount
from classes.starken.agency import Agency
from classes.starken.starken import SERV_CODE

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Agency(account=serv_acct).app_sync()
