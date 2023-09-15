import os
from typing import Any, Dict, List

from django.contrib.auth.models import User
from django.db.models import Q
from simple_history.utils import bulk_update_with_history

from app.delivery.models.delivery import Delivery as DelivMdl
from classes.mitocondria.mitocondria import Mitocondria
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class Delivery(Mitocondria):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @loggable
    @Mitocondria.conn_handling
    def search_all(self,
                   from_date: str,
                   *args,
                   **kwargs) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query_filepath = os.path.join(self.queries_folder_path,
                                      'search_all_deliv.sql')
        with open(file=query_filepath, mode='r') as file:
            query = file.read()
        query = query.format(schema=self.schema, from_date=from_date)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        headers = [header[0] for header in cursor.description]
        result = [dict(zip(headers, row)) for row in result]

        return result

    @loggable
    def app_sync(self, from_date: str, *args, **kwargs):
        model = DelivMdl
        delivs = self.search_all(from_date=from_date)
        user_obj = User.objects.get(username=APP_USERNAME)

        doc_types_equiv_by_code = self.doc_types_equiv_by_code
        deliv_types_equiv_by_code = self.deliv_types_equiv_by_code
        pay_types_equiv_by_code = self.pay_types_equiv_by_code

        for d in delivs:
            deliv_id = d['id']
            folio = d['folio']
            issue_date = d['issue_date']
            assy_date = issue_date
            rcpt_commit_date = d['commit_date']
            ship_st_and_num = d['ship_st_and_num']
            ship_complement = d['ship_addr_cpl'] or ''
            ship_dpto = d['ship_dpto'] or ''
            ship_muni_name = d['ship_muni_name']
            ordr_ref = d['ordr_ref']
            deliv_type_code = d['deliv_type_id']
            pay_type_code = d['pay_type_id']
            doc_types_code = d['doc_type'].split(',')
            doc_nums = d['doc_num'].split(',')

            print(deliv_id, folio, issue_date, assy_date, rcpt_commit_date, ship_st_and_num, ship_complement, ship_dpto, ship_muni_name, ordr_ref, deliv_type_code, pay_type_code, doc_types_code, doc_nums)

    # @loggable
    # def ways_search(self, *args, **kwargs) -> dict:
    #     cursor = self.connection.cursor()
    #     query = (
    #         "SELECT d.despachos_param_tipo_entrega_id id,"
    #         "d.despachos_param_tipo_entrega_nombre name "
    #         f"FROM {self.schema}.{self.shipping_type_model} d"
    #     )
    #     cursor.execute(query)
    #     results = cursor.fetchall()
    #     description = cursor.description
    #     cursor.close()
    #     self.disconnect()
    #     myresult = [
    #         dict(
    #             (description[i][0], value)
    #             for i, value in enumerate(row)
    #         ) for row in results
    #     ]

    #     return myresult

    # @loggable
    # def ways_sync(self, *args, **kwargs) -> None:
    #     ways = self.ways_search()
    #     for w in ways:
    #         id = w["id"]
    #         name = w["name"]
    #         object_search = DispWayMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             DispWayMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)

    # @loggable
    # def pay_types_search(self, *args, **kwargs) -> dict:
    #     cursor = self.connection.cursor()
    #     query = (
    #         "SELECT d.despachos_param_tipo_pago_id id,"
    #         "d.nombre_tipo_pago name "
    #         f"FROM {self.schema}.{self.shipping_pay_type_model} d"
    #     )
    #     cursor.execute(query)
    #     results = cursor.fetchall()
    #     description = cursor.description
    #     cursor.close()
    #     self.disconnect()
    #     myresult = [
    #         dict(
    #             (description[i][0], value)
    #             for i, value in enumerate(row)
    #         ) for row in results
    #     ]

    #     return myresult

    # @loggable
    # def pay_types_sync(self, *args, **kwargs) -> None:
    #     types = self.pay_types_search()
    #     for t in types:
    #         id = t['id']
    #         name = t['name']
    #         object_search = ShipPayTypeMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             ShipPayTypeMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)
