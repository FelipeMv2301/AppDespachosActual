from module.general.models.service_account import ServiceAccount
from classes.starken.branch import Branch
from classes.starken.starken import SERV_CODE

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    Branch(account=serv_acct).app_sync()
