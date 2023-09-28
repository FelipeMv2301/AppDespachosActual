from django.db import models
from simple_history.models import HistoricalRecords


class Muni(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    state = models.ForeignKey(to='general.State', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='municipality_history')
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
        db_table = 'municipality'
        ordering = [
            'code',
            'name',
            'enabled',
            'changed_by',
            'created_at',
            'updated_at',
        ]
