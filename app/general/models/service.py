from django.db import models
from simple_history.models import HistoricalRecords


class Service(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    is_carrier = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   related_name='general_serv_changed_by')
    history = HistoricalRecords(table_name='service_history')
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
        db_table = 'service'
        ordering = [
            'code',
            'name',
            'is_carrier',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
