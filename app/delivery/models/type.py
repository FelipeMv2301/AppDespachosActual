from django.db import models
from simple_history.models import HistoricalRecords


class Type(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   related_name='deliv_type_changed_by')
    history = HistoricalRecords(table_name='delivery_type_history')
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
        db_table = 'delivery_type'
        ordering = [
            'code',
            'name',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
