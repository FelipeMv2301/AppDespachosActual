from django.db import models
from django.utils import timezone
from django.core.signing import Signer
from simple_history.models import HistoricalRecords


class Account(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    desc = models.CharField(max_length=500)
    rut = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    cost_center = models.IntegerField()
    password = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    carrier = models.ForeignKey(to='delivery.Carrier',
                                on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(to='general.Company', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='account_history')
    # Object timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        db_table = 'account'

    def get_password(self, *args, **kwargs) -> str:
        pwd = self.password
        decrypted_pwd = Signer().unsign_object(pwd)

        return decrypted_pwd

    def get_api_key(self, *args, **kwargs) -> str:
        api_key = self.api_key
        decrypted_api_key = Signer().unsign_object(api_key)

        return decrypted_api_key
