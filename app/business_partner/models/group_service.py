from django.db import models
from simple_history.models import HistoricalRecords


class GroupService(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(to='business_partner.Group',
                              on_delete=models.CASCADE,
                              null=True)
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='business_partner_group_service_history')
    # Object timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        db_table = 'business_partner_group_service'
        ordering = [
            'code',
            'name',
            'group',
            'service_acct',
            'changed_by',
            'created_at',
            'updated_at',
        ]
