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
            SELECT
                subquery.id as id,
                group_concat(subquery.doc_num) as doc_nums,
                subquery.folio AS folio,
                subquery.issue_date AS issue_date,
                subquery.rcpt_date AS rcpt_date,
                subquery.from_mito AS from_mito,
                subquery.deliv_obs AS deliv_obss,
                subquery.deliv_opt AS deliv_opt,
                subquery.doc_num AS doc_num,
                subquery.ordr_updtd_commit_date AS ordr_updtd_commit_date,
                subquery.muni_name AS muni_name,
                subquery.state_code AS state_code,
                subquery.state_name AS state_name,
                subquery.ordr_obs AS ordr_obs,
                subquery.web_ordr_ref AS web_ordr_ref
            FROM
                (SELECT
                    d.id AS id,
                    d.created_at as create_date,
                    ROW_NUMBER() OVER(PARTITION BY ord.doc_num order by d.created_at) AS row_num,
                    d.folio AS folio,
                    d.issue_date AS issue_date,
                    d.rcpt_date AS rcpt_date,
                    d.from_mito AS from_mito,
                    og.deliv_obs AS deliv_obs,
                    CONCAT(serv.code, dt.code) AS deliv_opt,
                    ord.doc_num AS doc_num,
                    ord.create_date AS ordr_create_date,
                    ord.updtd_commit_date AS ordr_updtd_commit_date,
                    muni.name AS muni_name,
                    st.code AS state_code,
                    st.name AS state_name,
                    ord.obs AS ordr_obs,
                    ord.web_order_ref AS web_ordr_ref
                FROM
                    delivery d
                INNER JOIN delivery_status ds ON d.status_id = ds.id
                INNER JOIN order_delivery od ON d.id = od.delivery_id
                INNER JOIN order_grouping og ON od.order_grouping_id = og.id
                INNER JOIN delivery_option do ON og.delivery_option_id = do.id
                INNER JOIN service serv ON do.carrier_id = serv.id
                INNER JOIN delivery_type dt ON do.type_id = dt.id
                INNER JOIN address ad ON og.addr_id = ad.id
                INNER JOIN municipality muni ON ad.muni_id = muni.id
                INNER JOIN state st ON muni.state_id = st.id
                INNER JOIN `order` ord ON og.order_id = ord.id
                WHERE
                    ds.name != 'CANCEL'
                        AND ds.name != 'NOTISSUED'
                        AND d.issue_date >= '2023-09-10'
                        AND d.issue_date <= '2023-10-10'
                GROUP BY d.id , do.id , ad.id, ord.id, og.id
                HAVING deliv_opt != 'BQHOMEDELIV'
                ORDER BY ord.doc_num) AS subquery
                WHERE subquery.row_num = 1
            GROUP BY subquery.id, subquery.deliv_obs, subquery.deliv_opt, subquery.doc_num, subquery.ordr_updtd_commit_date, subquery.muni_name, subquery.state_code, subquery.ordr_obs, subquery.web_ordr_ref;
        """
        query = query.format(start_date=start_date_str, end_date=end_date_str)
        result = cls.objects.raw(query)

        return result
