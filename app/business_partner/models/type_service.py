from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class TypeService(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(to='business_partner.Type',
                             on_delete=models.CASCADE,
                             null=True)
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE,
                                     related_name='bsns_partner_type_serv_serv_acct')
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='business_partner_type_service_history')
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
        db_table = 'business_partner_type_service'
        ordering = [
            'code',
            'name',
            'type',
            'changed_by',
            'created_at',
            'updated_at',
        ]
