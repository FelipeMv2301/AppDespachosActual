from classes.starken.branch import Branch
from classes.starken.starken import Starken as Stk
from module.general.models.service_account import ServiceAccount

serv_accts = ServiceAccount.objects.filter(service__code=Stk.serv_code,
                                           enabled=True)
for serv_acct in serv_accts:
    Branch(account=serv_acct).app_sync()
