from module.general.models.service_account import ServiceAccount
from classes.sap.sales_person import SalesPerson
from classes.sap.sap import SERV_CODE

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    SalesPerson(account=serv_acct).app_sync()
