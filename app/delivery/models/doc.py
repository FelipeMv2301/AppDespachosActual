from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Document(models.Model):
    # General
    folio = models.CharField(max_length=100)
    delivery = models.ForeignKey(to='delivery.Delivery',
                                 on_delete=models.CASCADE)
    type = models.ForeignKey(to='delivery.DocumentType',
                             on_delete=models.CASCADE)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='delivery_document_history')
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
        db_table = 'delivery_document'
