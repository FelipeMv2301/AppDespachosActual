from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Option(models.Model):
    # Relationship
    carrier = models.ForeignKey(to='delivery.Carrier',
                                on_delete=models.CASCADE)
    service = models.ForeignKey(to='delivery.Service',
                                on_delete=models.CASCADE)
    type = models.ForeignKey(to='delivery.Type', on_delete=models.CASCADE)
    pay_type = models.ForeignKey(to='delivery.PayType',
                                 on_delete=models.CASCADE)
    agency = models.ForeignKey(to='delivery.Agency',
                               on_delete=models.CASCADE,
                               null=True)
    # Status
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='delivery_option_history')
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
        db_table = 'delivery_option'
