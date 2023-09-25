import json
import os
from typing import Any, Dict, List

from django.contrib.auth.models import User
from simple_history.utils import bulk_create_with_history

from app.delivery.models.agency import Agency
from app.delivery.models.carrier import Carrier
from app.delivery.models.delivery import Delivery as DelivMdl
from app.delivery.models.doc import Document
from app.delivery.models.doc_type import DocumentType
from app.delivery.models.opt import Option
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service
from app.delivery.models.type import Type
from app.general.models.address import Address
from app.general.models.muni_mito import MuniMito
from app.order.models.grouping import Grouping
from app.order.models.order import Order
from classes.mitocondria.mitocondria import Mitocondria
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError


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
        mdl = DelivMdl
        ordr_mdl = Order
        ordr_group_mdl = Grouping
        doc_mdl = Document
        addr_mdl = Address
        mito_muni_mdl = MuniMito
        doc_type_mdl = DocumentType
        pay_type_mdl = PayType
        type_mdl = Type
        serv_mdl = Service
        opt_mdl = Option
        carrier_mdl = Carrier
        ag_mdl = Agency
        delivs = self.search_all(from_date=from_date)
        user_obj = User.objects.get(username=APP_USERNAME)

        doc_types_equiv = {k: doc_type_mdl.objects.get(code=v)
                           for k, v in self.doc_types_equiv_by_code.items()}
        deliv_types_equiv = {k: type_mdl.objects.get(code=v)
                             for k, v in self.deliv_types_equiv_by_code.items()}
        pay_types_equiv = {k: pay_type_mdl.objects.get(code=v)
                           for k, v in self.pay_types_equiv_by_code.items()}
        service = serv_mdl.objects.get(code='NO')
        carrier = carrier_mdl.objects.get(code='STK')

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
            ordrs = [str(o['ref']) for o in json.loads(s=d['orders'])]
            deliv_type_code = d['deliv_type_id']
            pay_type_code = d['pay_type_id']
            height = d['height']
            width = d['width']
            length = d['length']
            weight = d['weight']
            packages = d['packages']
            valuation = d['valuation']
            docs = json.loads(s=d['docs'])

            try:
                deliv = mdl.objects.get(folio=folio)
                continue
            except mdl.DoesNotExist:
                pass

            try:
                ordr_objs = {o.ref: o
                             for o in ordr_mdl.objects.filter(ref__in=ordrs)}
                for ordr in ordrs:
                    if ordr not in ordr_objs:
                        e_msg = f'Error: order ref \'{ordr}\' '
                        e_msg += 'does not exist'
                        e_msg += f'\nFolio: {folio}'
                        e = CustomError(msg=e_msg)
                        raise e
            except CustomError:
                continue

            try:
                deliv_type = deliv_types_equiv[deliv_type_code]
            except KeyError:
                e_msg = f'Error: delivery type code \'{deliv_type_code}\' '
                e_msg += 'has no equivalence'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            try:
                pay_type = pay_types_equiv[pay_type_code]
            except KeyError:
                e_msg = f'Error: pay type code \'{pay_type_code}\' '
                e_msg += 'has no equivalence'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            if str(ship_muni_name).startswith('@'):
                ag_code = str(ship_muni_name).replace('@', '')
                try:
                    ag = (ag_mdl.objects
                          .select_related('addr')
                          .get(code=ag_code))
                    muni = ag.addr.muni
                except ag_mdl.DoesNotExist:
                    e_msg = f'Error: agency code \'{ag_code}\' '
                    e_msg += 'does not exist'
                    e_msg += f'\nFolio: {folio}'
                    CustomError(msg=e_msg)
                    continue
            else:
                ag = None
                try:
                    muni = mito_muni_mdl.objects.get(name=ship_muni_name)
                    muni = muni.muni
                except mito_muni_mdl.DoesNotExist:
                    e_msg = f'Error: ship muni name \'{ship_muni_name}\' '
                    e_msg += 'does not exist'
                    e_msg += f'\nFolio: {folio}'
                    CustomError(msg=e_msg)
                    continue

            opt = opt_mdl.objects.filter(
                enabled=True,
                carrier=carrier,
                service=service,
                type=deliv_type,
                pay_type=pay_type,
                agency=ag
            )
            if not opt:
                e_msg = 'Error: delivery option does not exist'
                e_msg += f'\nFolio: {folio}'
                e_msg += f'\nQuery: {opt.query}'
                CustomError(msg=e_msg)
                continue
            opt = opt.first()

            try:
                for doc in docs:
                    if not doc['folio']:
                        continue
                    doc_type_code = doc['type']
                    try:
                        doc['type'] = doc_types_equiv[doc_type_code]
                    except KeyError:
                        e_msg = f'Error: doc type code \'{doc_type_code}\' '
                        e_msg += 'has no equivalence'
                        e_msg += f'\nFolio: {folio}'
                        e = CustomError(msg=e_msg)
                        raise e
            except CustomError:
                continue

            addr = addr_mdl(
                st_and_num=ship_st_and_num,
                complement=f'{ship_complement} {ship_dpto}',
                muni=muni,
                changed_by=user_obj
            )
            addr = bulk_create_with_history(objs=[addr],
                                            model=addr_mdl)[0]

            ordr_groups_to_create = []
            for ordr in ordrs:
                ordr_groups_to_create.append(ordr_group_mdl(
                    order=ordr_objs[ordr],
                    delivery_option=opt,
                    addr=addr,
                    changed_by=user_obj
                ))
            ordr_groups = bulk_create_with_history(
                objs=ordr_groups_to_create,
                model=ordr_group_mdl
            )

            deliv = mdl(
                folio=folio,
                issue_date=issue_date,
                assembly_date=assy_date,
                rcpt_commit_date=rcpt_commit_date,
                mito_id=deliv_id,
                from_mito=True,
                height=height,
                width=width,
                length=length,
                weight=weight,
                packages_qty=packages,
                valuation=valuation,
                changed_by=user_obj
            )
            deliv = bulk_create_with_history(
                objs=[deliv],
                model=mdl
            )[0]

            for ordr_group in ordr_groups:
                deliv.order_delivery.add(ordr_group)

            for doc in docs:
                doc_folio = doc['folio']
                if not doc_folio:
                    continue
                doc_type = doc['type']
                bulk_create_with_history(
                    objs=[doc_mdl(folio=doc_folio,
                                  delivery=deliv,
                                  type=doc_type,
                                  changed_by=user_obj)],
                    model=doc_mdl
                )
