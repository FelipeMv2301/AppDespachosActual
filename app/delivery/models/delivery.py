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
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE,
                                     null=True)
    # Dates
    issue_date = models.DateField(default=timezone.now)
    assembly_date = models.DateField()
    rcpt_commit_date = models.DateField(null=True)
    rcpt_date = models.DateField(null=True)
    # Dimensions and weight
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    weight = models.FloatField()
    # Packages
    packages_qty = models.IntegerField()
    # Valuation
    valuation = models.FloatField()
    # Status
    status = models.ForeignKey(to='delivery.Status',
                               on_delete=models.CASCADE,
                               null=True)
    service_status = models.CharField(max_length=100, null=True)
    locked = models.BooleanField(default=False)
    # Mitocondria info
    mito_id = models.IntegerField(null=True)
    from_mito = models.BooleanField(default=False)
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
        ordering = [
            'folio',
            'service_acct',
            'issue_date',
            'assembly_date',
            'rcpt_commit_date',
            'rcpt_date',
            'height',
            'width',
            'length',
            'weight',
            'packages_qty',
            'valuation',
            'status',
            'service_status',
            'locked',
            'mito_id',
            'from_mito',
            'changed_by',
            'created_at',
            'updated_at',
        ]
        permissions = [
            (
                'view_kpis',
                'Can view KPIs',
            ),
            (
                'edit_delivery',
                'Can edit delivery',
            ),
            (
                'edit_delivery_rcpt_date',
                'Can edit delivery reception date',
            ),
            (
                'issue_delivery',
                'Can issue delivery',
            ),
            (
                'cancel_delivery',
                'Can cancel delivery',
            ),
            (
                'view_delivery_panel',
                'Can view delivery panel',
            ),
        ]
