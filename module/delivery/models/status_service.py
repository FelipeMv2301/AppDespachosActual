from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class StatusService(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    status = models.ForeignKey(to='delivery.Status',
                               on_delete=models.CASCADE,
                               null=True)
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE,
                                     related_name='delivery_status_serv_serv_acct')
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   related_name='delivery_status_serv_changed_by')
    history = HistoricalRecords(table_name='delivery_status_service_history')
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
        db_table = 'delivery_status_service'
        ordering = [
            'code',
            'name',
            'status',
            'service_acct',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
