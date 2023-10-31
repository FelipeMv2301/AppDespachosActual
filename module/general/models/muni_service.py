from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class MuniService(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    muni = models.ForeignKey(to='general.Muni',
                             on_delete=models.CASCADE,
                             null=True)
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE)
    to_pay = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='municipality_service_history')
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
        db_table = 'municipality_service'
        ordering = [
            'code',
            'name',
            'muni',
            'service_acct',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
