import random
import string

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Employee(models.Model):
    @staticmethod
    def new_code():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Employee.objects.count() == 0:
            correlative = 1
        else:
            correlative = Employee.objects.latest('id').id + 1
        folio = f'{prefix}{correlative}'
        return folio

    # General
    code = models.CharField(max_length=100,
                            unique=True,
                            default=new_code.__func__)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='employee_history')
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
        db_table = 'employee'
        ordering = [
            'code',
            'first_name',
            'last_name',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
