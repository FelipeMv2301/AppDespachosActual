import random
import string

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Receiver(models.Model):
    @staticmethod
    def new_code():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Receiver.objects.count() == 0:
            correlative = 1
        else:
            correlative = Receiver.objects.latest('id').id + 1
        code = f'{prefix}{correlative}'
        return code

    # General
    code = models.CharField(max_length=100,
                            unique=True,
                            default=new_code.__func__)
    reference = models.CharField(max_length=100, default=new_code.__func__)
    name = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100)
    delivery = models.ForeignKey(to='delivery.Delivery',
                                 on_delete=models.CASCADE)
    # Status
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='delivery_receiver_history')
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
        db_table = 'delivery_receiver'
