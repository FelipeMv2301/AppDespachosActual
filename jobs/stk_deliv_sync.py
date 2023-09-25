from app.delivery.models.account import Account
from classes.starken.delivery import Delivery
from classes.starken.starken import Starken

accts = Account.objects.filter(carrier__code=Starken().carrier_code)
for acct in accts:
    Delivery(account=acct).app_sync()
