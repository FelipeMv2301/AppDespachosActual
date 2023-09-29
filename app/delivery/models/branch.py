from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Branch(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE)
    addr = models.ForeignKey(to='general.Address', on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=100, null=True)
    shipping = models.BooleanField(default=True)
    delivery = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='branch_history')
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
        db_table = 'branch'
        ordering = [
            'code',
            'name',
            'service_acct',
            'addr',
            'phone',
            'phone2',
            'shipping',
            'delivery',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
