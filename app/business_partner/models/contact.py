import random
import string

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Contact(models.Model):
    @staticmethod
    def new_code():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Contact.objects.count() == 0:
            correlative = 1
        else:
            correlative = Contact.objects.latest('id').id + 1
        code = f'{prefix}{correlative}'
        return code

    # General
    code = models.CharField(max_length=100,
                            unique=True,
                            default=new_code.__func__)
    reference = models.CharField(max_length=100, default=new_code.__func__)
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
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        db_table = 'contact'
        ordering = [
            'code',
            'reference',
            'first_name',
            'last_name',
            'addr',
            'phone1',
            'phone2',
            'mobile_phone',
            'email_addr',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
