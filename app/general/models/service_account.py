from django.core.signing import Signer
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class ServiceAccount(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    rut = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    number = models.CharField(max_length=100, null=True)
    cost_center = models.IntegerField(null=True)
    password = models.CharField(max_length=100, null=True)
    api_key = models.CharField(max_length=100, null=True)
    database = models.CharField(max_length=100, null=True)
    host = models.CharField(max_length=100, null=True)
    port = models.CharField(max_length=100, null=True)
    service = models.ForeignKey(to='general.Service',
                                on_delete=models.CASCADE)
    company = models.ForeignKey(to='general.Company', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='service_account_history')
    # Object timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        db_table = 'service_account'
        ordering = [
            'code',
            'reference',
            'name',
            'desc',
            'rut',
            'username',
            'number',
            'cost_center',
            'password',
            'api_key',
            'database',
            'host',
            'port',
            'service',
            'company',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]

    def get_password(self, *args, **kwargs) -> str:
        pwd = self.password
        decrypted_pwd = Signer().unsign_object(pwd)

        return decrypted_pwd

    def get_api_key(self, *args, **kwargs) -> str:
        api_key = self.api_key
        decrypted_api_key = Signer().unsign_object(api_key)

        return decrypted_api_key
