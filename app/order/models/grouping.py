from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Grouping(models.Model):
    code = models.CharField(max_length=100)
    # Relationship
    order = models.ForeignKey(to='order.Order',
                              on_delete=models.CASCADE)
    delivery_option = models.ForeignKey(to='delivery.Option',
                                        on_delete=models.CASCADE)
    addr = models.ForeignKey(to='general.Address',
                             on_delete=models.CASCADE)
    # Status
    enabled = models.BooleanField(default=True)
    # Observations
    deliv_obs = models.TextField(null=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='order_grouping_history')
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
        db_table = 'order_grouping'
