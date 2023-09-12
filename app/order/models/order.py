from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Order(models.Model):
    # General
    ref = models.CharField(max_length=100, unique=True)
    currency = models.ForeignKey(to='general.Currency',
                                 on_delete=models.CASCADE)
    web_order_ref = models.CharField(max_length=100)
    sale_channel = models.ForeignKey(to='order.SaleChannel',
                                     on_delete=models.CASCADE)
    seller = models.ForeignKey(to='general.Employee',
                               on_delete=models.CASCADE)
    # Dates
    create_date = models.DateField()
    tax_date = models.DateField()
    commit_date = models.DateField()
    updtd_commit_date = models.DateField()
    # Adresses
    ship_addr = models.ForeignKey(to='general.Address',
                                  on_delete=models.CASCADE,
                                  related_name='order_ship_addr')
    bill_addr = models.ForeignKey(to='general.Address',
                                  on_delete=models.CASCADE,
                                  related_name='order_bill_addr')
    # Customer
    customer = models.ForeignKey(to='business_partner.BusinessPartner',
                                 on_delete=models.CASCADE)
    # Customer contact
    contact = models.ForeignKey(to='business_partner.contact',
                                on_delete=models.CASCADE)
    # Totals
    local_total_dcnt = models.IntegerField()
    doc_total_dcnt = models.IntegerField()
    local_total_tax = models.IntegerField()
    doc_total_tax = models.IntegerField()
    local_total_amt = models.IntegerField()
    doc_total_amt = models.IntegerField()
    # Status
    enabled = models.BooleanField(default=True)
    # Observations
    obs = models.TextField()
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   null=True)
    history = HistoricalRecords(table_name='order_history')
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
        db_table = 'order'
