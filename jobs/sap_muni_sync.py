from module.general.models.service_account import ServiceAccount
from classes.sap.muni_and_city import MunicipalityAndCity
from classes.sap.sap import SERV_CODE

serv_accts = ServiceAccount.objects.filter(service__code=SERV_CODE,
                                           enabled=True)
for serv_acct in serv_accts:
    MunicipalityAndCity(account=serv_acct).app_sync()
