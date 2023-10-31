import json
import os
from typing import Any, Dict, List

from django.contrib.auth.models import User

from module.delivery.models.branch import Branch
from module.delivery.models.delivery import Delivery as DelivMdl
from module.delivery.models.doc import Document
from module.delivery.models.doc_type import DocumentType
from module.delivery.models.opt import Option
from module.delivery.models.pay_type import PayType
from module.delivery.models.service import Service as DelivService
from module.delivery.models.status import Status
from module.delivery.models.type import Type
from module.general.models.address import Address
from module.general.models.muni import Muni
from module.general.models.service_account import ServiceAccount
from module.order.models.grouping import Grouping
from module.order.models.order import Order
from classes.despachos.despachos import Despachos
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError
from project.settings.base import APP_USERNAME


class Delivery(Despachos):
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        super().__init__(account=account, *args, **kwargs)

    @loggable
    @Despachos.conn_handling
    def search_all(self, *args, **kwargs) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query_filepath = os.path.join(self.queries_folder_path,
                                      'search_all_deliv.sql')
        with open(file=query_filepath, mode='r') as file:
            query = file.read()
        query = query.format(schema=self.schema)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        headers = [header[0] for header in cursor.description]
        result = [dict(zip(headers, row)) for row in result]

        return result

    @loggable
    def app_sync(self, *args, **kwargs):
        delivs = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        serv_accts = {}
        servs = {}
        s_accts = (ServiceAccount.objects.select_related('service')
                   .filter(code__in=['STKBQ01', 'CHILEXBQ01', 'BQ01',
                                     'BLUEXBQ01', 'UNKBQ01']))
        for sa in s_accts:
            serv = sa.service
            serv_accts[serv.code] = sa
            servs[serv.code] = serv
        statuss = {s.code: s
                   for s in (Status.objects
                             .filter(code__in=['ISSUED', 'CANCEL', 'RCVD']))}
        deliv_service = DelivService.objects.get(code='NO')
        doc_types = {str(dt.code): dt
                     for dt in (DocumentType.objects
                                .filter(code__in=['33', '39', '52']))}
        deliv_types = {dt.code: dt for dt in Type.objects.all()}
        pay_types = {dpt.code: dpt for dpt in PayType.objects.all()}

        for d in delivs:
            folio = d['folio']
            issue_date = d['issue_date']
            assy_date = d['assembly_date']
            rcpt_commit_date = d['rcpt_commit_date']
            rcpt_date = d['rcpt_date']
            is_complete = d['is_complete']
            deliv_obs = d['deliv_obs']
            ship_st_and_num = d['st_and_num']
            ship_muni_utc_code = d['muni_utc_code']
            ordr_doc_num = d['doc_num']
            status_code = str(d['status_code'])
            if status_code == 'NOTISSUED' or not issue_date:
                continue
            deliv_type_code = str(d['deliv_type_code'])
            # to_branch = deliv_type_code == 'BRDELIV'
            pay_type_code = str(d['pay_type_code'])
            serv_code = str(d['serv_code'])
            branch_code = d['branch_serv_code']
            docs = json.loads(s=d['docs'])

            if serv_code == 'BQ':
                deliv_type_code = 'BRDELIV'
                branch_code = 'BQ301'
            elif branch_code:
                deliv_type_code = 'BRDELIV'
            else:
                deliv_type_code = 'HOMEDELIV'

            try:
                deliv = DelivMdl.objects.get(folio=folio)
                continue
            except DelivMdl.DoesNotExist:
                pass

            try:
                ordr = Order.objects.get(doc_num=ordr_doc_num)
            except Order.DoesNotExist:
                e_msg = f'Error: order ref \'{ordr_doc_num}\' '
                e_msg += 'does not exist'
                e_msg += f'\nFolio: {folio}'
                e = CustomError(msg=e_msg)
                continue

            try:
                status = statuss[status_code]
            except KeyError:
                e_msg = f'Error: status code \'{status_code}\' '
                e_msg += 'does not exist'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            try:
                deliv_type = deliv_types[deliv_type_code]
            except KeyError:
                e_msg = f'Error: delivery type code \'{deliv_type_code}\' '
                e_msg += 'does not exist'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            try:
                pay_type = pay_types[pay_type_code]
            except KeyError:
                e_msg = f'Error: pay type code \'{pay_type_code}\' '
                e_msg += 'does not exist'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            try:
                service = servs[serv_code]
            except KeyError:
                e_msg = f'Error: service code \'{serv_code}\' '
                e_msg += 'does not exist'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            try:
                serv_acct = serv_accts[serv_code]
            except KeyError:
                e_msg = 'Error: service account for service code '
                e_msg += f'\'{serv_code}\' does not exist'
                e_msg += f'\nFolio: {folio}'
                CustomError(msg=e_msg)
                continue

            if deliv_type_code != 'BRDELIV':
                branch = None
                try:
                    muni = Muni.objects.get(code=ship_muni_utc_code)
                except Muni.DoesNotExist:
                    e_msg = f'Error: ship muni code \'{ship_muni_utc_code}\' '
                    e_msg += 'does not exist'
                    e_msg += f'\nFolio: {folio}'
                    CustomError(msg=e_msg)
                    continue
            else:
                try:
                    branch = (Branch.objects
                              .select_related('addr', 'addr__muni')
                              .get(code=branch_code, service_acct=serv_acct))
                    muni = branch.addr.muni
                except Branch.DoesNotExist:
                    e_msg = f'Error: branch code \'{branch_code}\' '
                    e_msg += f'for serv acct code \'{serv_acct.code}\' '
                    e_msg += 'does not exist'
                    e_msg += f'\nFolio: {folio}'
                    CustomError(msg=e_msg)
                    continue

            opt = Option.objects.filter(
                # enabled=True,
                carrier=service,
                service=deliv_service,
                type=deliv_type,
                pay_type=pay_type,
                branch=branch
            )
            if not opt:
                e_msg = 'Error: delivery option does not exist'
                e_msg += f'\nFolio: {folio}'
                # e_msg += f'\nQuery: {opt.query}'
                CustomError(msg=e_msg)
                continue
            opt = opt.first()

            try:
                for doc in docs:
                    if not doc['folio']:
                        continue
                    doc_type_code = str(doc['doc_code'])
                    try:
                        doc['type'] = doc_types[doc_type_code]
                    except KeyError:
                        e_msg = f'Error: doc type code \'{doc_type_code}\' '
                        e_msg += 'does not exist'
                        e_msg += f'\nFolio: {folio}'
                        e = CustomError(msg=e_msg)
                        raise e
            except CustomError:
                continue

            addr = Address.objects.create(
                st_and_num=ship_st_and_num,
                muni=muni,
                changed_by=user_obj
            )

            ordr_group_code = Grouping.new_code()
            ordr_group = Grouping.objects.create(
                code=ordr_group_code,
                order=ordr,
                delivery_option=opt,
                addr=addr,
                contact=ordr.contact,
                customer=ordr.customer,
                deliv_obs=deliv_obs,
                changed_by=user_obj,
                enabled=False,
            )

            deliv = DelivMdl.objects.create(
                folio=folio,
                service_acct=serv_acct,
                issue_date=issue_date,
                assembly_date=assy_date,
                rcpt_commit_date=rcpt_commit_date,
                rcpt_date=rcpt_date,
                height=0,
                width=0,
                length=0,
                weight=0,
                packages_qty=0,
                valuation=0,
                status=status,
                is_complete=is_complete,
                locked=True,
                changed_by=user_obj
            )

            deliv.order_delivery.add(ordr_group)

            for doc in docs:
                doc_folio = doc['folio']
                if not doc_folio:
                    continue
                doc_type = doc['type']
                Document.objects.create(
                    folio=doc_folio,
                    delivery=deliv,
                    type=doc_type,
                    changed_by=user_obj
                )
