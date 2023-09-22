from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class OrderDelivery(models.Model):
    # Relationship
    order_grouping = models.ForeignKey(to='order.Grouping',
                                       on_delete=models.CASCADE)
    delivery = models.ForeignKey(to='delivery.Delivery',
                                 on_delete=models.CASCADE)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='order_delivery_history')
    # Object
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        db_table = 'order_delivery'
