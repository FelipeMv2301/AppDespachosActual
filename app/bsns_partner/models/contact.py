from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Contact(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    ref = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    # Address info
    addr = models.ForeignKey(to='general.Address', on_delete=models.CASCADE)
    # Contact info
    phone1 = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=100, null=True)
    mobile_phone = models.CharField(max_length=100, null=True)
    email_addr = models.EmailField(max_length=100, null=True)
    # Status
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='contact_history')
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
        db_table = 'contact'
