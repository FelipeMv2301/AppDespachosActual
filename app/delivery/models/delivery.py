import random
import string

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Delivery(models.Model):
    @staticmethod
    def new_folio():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Delivery.objects.count() == 0:
            correlative = 1
        else:
            correlative = Delivery.objects.latest('id').id + 1
        folio = f'{prefix}{correlative}'
        return folio

    # General
    folio = models.CharField(max_length=100,
                             default=new_folio.__func__,
                             unique=True)
    order_delivery = models.ManyToManyField(to='order.Grouping',
                                            through='order.OrderDelivery')
    status = models.ForeignKey(to='delivery.Status',
                               on_delete=models.CASCADE,
                               null=True)
    third_status = models.CharField(max_length=100, null=True)
    account = models.ForeignKey(to='delivery.Account',
                                on_delete=models.CASCADE,
                                null=True)
    # Dates
    issue_date = models.DateField(default=timezone.now)
    assembly_date = models.DateField()
    rcpt_commit_date = models.DateField(null=True)
    rcpt_date = models.DateField(null=True)
    # Mitocondria info
    mito_id = models.IntegerField(null=True)
    from_mito = models.BooleanField(default=False)
    # Dimensions and weight
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    weight = models.FloatField()
    # Packages
    packages_qty = models.IntegerField()
    # Valuation
    valuation = models.FloatField()
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='delivery_history')
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
        db_table = 'delivery'
