import random
import string

from django.db import models
from django.db.models.query import RawQuerySet
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Grouping(models.Model):
    @staticmethod
    def new_code():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Grouping.objects.count() == 0:
            correlative = 1
        else:
            correlative = Grouping.objects.latest('id').id + 1
        code = f'{prefix}{correlative}'
        return code

    code = models.CharField(max_length=100)
    # Relationship
    order = models.ForeignKey(to='order.Order',
                              on_delete=models.CASCADE)
    delivery_option = models.ForeignKey(to='delivery.Option',
                                        on_delete=models.CASCADE)
    addr = models.ForeignKey(to='general.Address',
                             on_delete=models.CASCADE)
    customer = models.ForeignKey(to='business_partner.BusinessPartner',
                                 on_delete=models.CASCADE)
    contact = models.ForeignKey(to='business_partner.Contact',
                                on_delete=models.CASCADE)
    # Status
    enabled = models.BooleanField(default=True)
    # Observations
    deliv_obs = models.TextField(null=True)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='order_grouping_history')
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
        db_table = 'order_grouping'
        ordering = [
            'code',
            'order',
            'delivery_option',
            'addr',
            'customer',
            'contact',
            'enabled',
            'deliv_obs',
            'changed_by',
            'created_at',
            'updated_at',
        ]

    @classmethod
    def query_for_delivery_issue(cls,
                                 ordr_doc_num: str,
                                 *args,
                                 **kwargs) -> RawQuerySet:
        query = """
            WITH q AS (
                SELECT
                    MAX(og.id) id,
                    GROUP_CONCAT(o.doc_num) doc_nums
                FROM
                    order_grouping og
                        INNER JOIN
                    `order` o ON og.order_id = o.id
                GROUP BY og.code
                HAVING doc_nums LIKE '%%{ordr_doc_num}%%'
            )
            SELECT
                MAX(q.id) id,
                q.doc_nums doc_nums
            FROM q
            GROUP BY q.doc_nums
        """
        query = query.format(ordr_doc_num=ordr_doc_num)
        result = cls.objects.raw(query)

        return result
