from typing import List

from django.db import models
from django.db.models.query import RawQuerySet
from django.utils import timezone


class OrderDelivery(models.Model):
    # Relationship
    order_grouping = models.ForeignKey(to='order.Grouping',
                                       on_delete=models.CASCADE)
    delivery = models.ForeignKey(to='delivery.Delivery',
                                 on_delete=models.CASCADE)
    # Object tracking
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'order_delivery'

    @classmethod
    def query_for_delivery_review(cls,
                                  ordr_doc_nums: List[str],
                                  *args,
                                  **kwargs) -> RawQuerySet:
        query = """
            SELECT
                d.id id,
                d.folio folio,
                GROUP_CONCAT(o.doc_num) doc_nums,
                d.assembly_date assy_date,
                d.issue_date issue_date,
                d.rcpt_commit_date rcpt_commit_date,
                d.rcpt_date rcpt_date,
                CASE
                    WHEN d.is_complete IS TRUE THEN 'Sí'
                    ELSE 'No'
                END is_complete,
                dst.name status,
                dst.code status_code,
                d.locked locked,
                d.service_status serv_status,
                CASE
                    WHEN d.from_mito IS TRUE THEN 'App Mitocondria'
                    ELSE 'App'
                END source,
                m.name muni,
                s.name carrier,
                s.code carrier_code,
                dt.name deliv_type,
                dpt.name deliv_pay_type,
                ds.name deliv_service,
                CASE
                    WHEN b.name IS NULL THEN 'No aplica'
                    ELSE b.name
                END branch
            FROM
                order_delivery od
                    LEFT JOIN
                delivery d ON od.delivery_id = d.id
                    LEFT JOIN
                delivery_status dst ON d.status_id = dst.id
                    LEFT JOIN
                order_grouping og ON od.order_grouping_id = og.id
                    LEFT JOIN
                address a ON og.addr_id = a.id
                    LEFT JOIN
                municipality m ON a.muni_id = m.id
                    LEFT JOIN
                `order` o ON og.order_id = o.id
                    LEFT JOIN
                delivery_option do ON og.delivery_option_id = do.id
                    LEFT JOIN
                service s ON do.carrier_id = s.id
                    LEFT JOIN
                delivery_type dt ON do.type_id = dt.id
                    LEFT JOIN
                delivery_pay_type dpt ON do.pay_type_id = dpt.id
                    LEFT JOIN
                delivery_service ds ON do.service_id = ds.id
                    LEFT JOIN
                branch b ON do.branch_id = b.id
            WHERE o.doc_num IN ({ordr_doc_nums})
            GROUP BY d.folio , m.name , s.id , dt.name , dpt.name , ds.name , b.name;
        """
        query = query.format(ordr_doc_nums=','.join(ordr_doc_nums))
        result = cls.objects.raw(query)

        return result
