import random
import string

from django.db import models
from simple_history.models import HistoricalRecords


class Address(models.Model):
    @staticmethod
    def new_code():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Address.objects.count() == 0:
            correlative = 1
        else:
            correlative = Address.objects.latest('id').id + 1
        folio = f'{prefix}{correlative}'
        return folio

    # General
    code = models.CharField(max_length=100,
                            unique=True,
                            default=new_code.__func__)
    reference = models.CharField(max_length=100, default=new_code.__func__)
    st_and_num = models.CharField(max_length=500)
    complement = models.CharField(max_length=500, null=True)
    muni = models.ForeignKey(to='general.Muni',
                             on_delete=models.CASCADE,
                             null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='address_history')
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
        db_table = 'address'
        ordering = [
            'code',
            'reference',
            'st_and_num',
            'complement',
            'muni',
            'latitude',
            'longitude',
            'changed_by',
            'created_at',
            'updated_at',
        ]
