from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class TypeCarrier(models.Model):
    # General
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(to='delivery.Type',
                             on_delete=models.CASCADE,
                             null=True)
    carrier = models.ForeignKey(to='delivery.Carrier',
                                on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   related_name='deliv_type_carrier_changed_by')
    history = HistoricalRecords(table_name='delivery_type_carrier_history')
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
        db_table = 'delivery_type_carrier'
