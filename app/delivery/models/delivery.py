import random
import string
from datetime import date

from django.db import models
from django.db.models.query import RawQuerySet
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Delivery(models.Model):
    @staticmethod
    def new_folio():
        chars = string.ascii_uppercase
        prefix = ''.join(random.choice(chars) for _ in range(4))
        if Delivery.objects.count() == 0:
            correlative = 1
        else:
            correlative = Delivery.objects.latest('id').id + 1
        folio = f'{prefix}{correlative}'
        return folio

    # General
    folio = models.CharField(max_length=100,
                             default=new_folio.__func__,
                             unique=True)
    order_delivery = models.ManyToManyField(to='order.Grouping',
                                            through='order.OrderDelivery')
    service_acct = models.ForeignKey(to='general.ServiceAccount',
                                     on_delete=models.CASCADE,
                                     null=True)
    # Dates
    issue_date = models.DateField(default=timezone.now)
    assembly_date = models.DateField()
    rcpt_commit_date = models.DateField(null=True)
    rcpt_date = models.DateField(null=True)
    # Dimensions and weight
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    weight = models.FloatField()
    # Packages
    packages_qty = models.IntegerField()
    # Valuation
    valuation = models.FloatField()
    # Status
    status = models.ForeignKey(to='delivery.Status',
                               on_delete=models.CASCADE,
                               null=True)
    service_status = models.CharField(max_length=100, null=True)
    is_complete = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    # Mitocondria info
    mito_id = models.IntegerField(null=True)
    from_mito = models.BooleanField(default=False)
    # Object tracking
    changed_by = models.ForeignKey(to='auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='delivery_history')
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
        db_table = 'delivery'
        ordering = [
            'folio',
            'service_acct',
            'issue_date',
            'assembly_date',
            'rcpt_commit_date',
            'rcpt_date',
            'height',
            'width',
            'length',
            'weight',
            'packages_qty',
            'valuation',
            'status',
            'service_status',
            'is_complete',
            'locked',
            'mito_id',
            'from_mito',
            'changed_by',
            'created_at',
            'updated_at',
        ]
        permissions = [
            (
                'view_kpis',
                'Can view KPIs',
            ),
            (
                'edit_delivery',
                'Can edit delivery',
            ),
            (
                'edit_deliv_rcpt_date',
                'Can edit delivery reception date',
            ),
            (
                'issue_delivery',
                'Can issue delivery',
            ),
            (
                'cancel_delivery',
                'Can cancel delivery',
            ),
            (
                'view_delivery_panel',
                'Can view delivery panel',
            ),
        ]

    @classmethod
    def query_for_stat(cls,
                       start_date: date,
                       end_date: date,
                       *args,
                       **kwargs) -> RawQuerySet:
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        query = """
            WITH q AS (
                SELECT
                    d.id AS id,
                    ordr.doc_num AS doc_num,
                    ordr.create_date AS ordr_create_date,
                    ordr.commit_date AS ordr_commit_date,
                    ordr.updtd_commit_date AS ordr_updtd_commit_date,
                    ordr.obs AS ordr_obs,
                    ordr.web_order_ref AS web_ordr_ref,
                    d.folio AS folio,
                    d.assembly_date AS assy_date,
                    d.issue_date AS issue_date,
                    d.is_complete AS is_complete,
                    status.name AS status_name,
                    d.service_status AS status_serv_name,
                    dt.name AS deliv_type_name,
                    serv.name AS service_name,
                    muni.name AS muni_name,
                    state.name AS state_name,
                    d.rcpt_date AS rcpt_date,
                    d.from_mito AS from_mito,
                    og.deliv_obs AS deliv_obs,
                    ROW_NUMBER() OVER(PARTITION BY ordr.doc_num ORDER BY d.created_at) AS row_num
                FROM delivery d
                    INNER JOIN delivery_status status ON d.status_id = status.id
                    INNER JOIN order_delivery od ON d.id = od.delivery_id
                    INNER JOIN order_grouping og ON od.order_grouping_id = og.id
                    INNER JOIN address addr ON og.addr_id = addr.id
                    INNER JOIN municipality muni ON addr.muni_id = muni.id
                    INNER JOIN state state ON muni.state_id = state.id
                    INNER JOIN `order` ordr ON og.order_id = ordr.id
                    INNER JOIN delivery_option do ON og.delivery_option_id = do.id
                    INNER JOIN service serv ON do.carrier_id = serv.id
                    INNER JOIN delivery_type dt ON do.type_id = dt.id
                WHERE
                    status.name != 'CANCEL' AND
                    status.name != 'NOTISSUED' AND
                    d.issue_date >= '2022-09-10' AND
                    d.issue_date <= '2023-12-10'
                ORDER BY d.created_at ASC)
                SELECT *
                FROM q
                WHERE q.row_num = 1;
        """
        query = query.format(start_date=start_date_str, end_date=end_date_str)
        result = cls.objects.raw(query)

        return result
