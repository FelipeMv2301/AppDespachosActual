from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Service(models.Model):
    # General
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User',
                                   on_delete=models.CASCADE,
                                   related_name='deliv_serv_changed_by')
    history = HistoricalRecords(table_name='delivery_service_history')
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
        db_table = 'delivery_service'
