from django.db import models
from simple_history.models import HistoricalRecords


class BusinessPartner(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(to='general.Currency',
                                 on_delete=models.CASCADE)
    group = models.ForeignKey(to='business_partner.Group',
                              on_delete=models.CASCADE)
    tax_id = models.CharField(max_length=100)
    type = models.ForeignKey(to='business_partner.Type',
                             on_delete=models.CASCADE,
                             null=True)
    # Contact info
    phone1 = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=100, null=True)
    mobile_phone = models.CharField(max_length=100, null=True)
    email_addr = models.EmailField(max_length=100, null=True)
    # Status
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='business_partner_history')
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
        db_table = 'business_partner'
        ordering = [
            'code',
            'name',
            'currency',
            'group',
            'tax_id',
            'type',
            'phone1',
            'phone2',
            'mobile_phone',
            'email_addr',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
