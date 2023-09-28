import json
import traceback
from typing import Any, Dict

import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.business_partner.models.bsns_partner import BusinessPartner
from app.business_partner.models.contact import Contact
from app.business_partner.models.group_service import GroupService
from app.business_partner.models.type_service import TypeService
from app.general.models.address import Address
from app.general.models.currency_service import CurrencyService
from app.general.models.employee_service import EmployeeService
from app.general.models.muni_service import MuniService
from app.general.models.service_account import ServiceAccount
from app.order.models.order import Order as OrderMdl
from app.order.models.sale_channel_service import SaleChannelService
from classes.sap.sap import Sap
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class Order(Sap):
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        super().__init__(account=account, *args, **kwargs)

    @loggable
    @Sap.session_handling
    def search_all(self, from_date: str, *args, **kwargs) -> Dict[str, Any]:
        mdl = self.order_mdl
        order_addr_mdl = self.order_addrs_mdl
        bsns_partner_mdl = self.bsns_partner_mdl
        bsns_partner_contact_mdl = self.bsns_partner_contact_mdl

        url = self.host
        url += f'$crossjoin({mdl}, {order_addr_mdl}, {bsns_partner_mdl}, '
        url += f'{bsns_partner_contact_mdl})?$expand={mdl}($select=DocNum, '
        url += 'DocCurrency, DocDate, DocDueDate, TaxDate, U_WedDocNum, '
        url += 'U_TipoVenta, CardName, DocumentStatus, Cancelled'
        url += 'ContactPersonCode, SalesPersonCode, DocTotal, '
        url += 'DocTotalSys,  VatSum, VatSumSys, TotalDiscount, ShipToCode, '
        url += f'PayToCode),{order_addr_mdl}($select=ShipToStreet, '
        url += f'ShipToCounty, BillToStreet, BillToCounty),{bsns_partner_mdl}'
        url += '($select=CardCode, GroupCode, Currency, CardName, CardType, '
        url += 'FederalTaxID, Phone1, Phone2, EmailAddress),'
        url += f'{bsns_partner_contact_mdl}($select=E_Mail, MobilePhone, '
        url += 'FirstName, MiddleName, LastName, Name, Phone1, Phone2, Address'
        url += f')&$filter={mdl}/DocEntry eq {order_addr_mdl}/DocEntry and '
        url += f'{mdl}/CardCode eq  {bsns_partner_mdl}/CardCode and '
        url += f'{mdl}/ContactPersonCode eq {bsns_partner_contact_mdl}/'
        url += f'InternalCode and {mdl}/UpdateDate ge \'{from_date}\' and '
        # url += f'{mdl}/DocumentStatus eq \'O\' and '
        # url += f'{mdl}/Cancelled eq \'tNO\''
        url += f'&$orderby={mdl}/DocEntry asc'

        self.change_max_page_size(qty=3000)
        response = requests.get(url=url, headers=self.headers)
        self.check_response(response=response)

        return json.loads(s=response.text)['value']

    @loggable
    def app_sync(self, from_date: str, *args, **kwargs):
        mdl = OrderMdl
        addr_mdl = Address
        bsns_partner_mdl = BusinessPartner
        contact_mdl = Contact
        group_mdl = GroupService
        type_mdl = TypeService
        ccy_mdl = CurrencyService
        sale_channel_mdl = SaleChannelService
        employee_mdl = EmployeeService
        muni_mdl = MuniService

        sap_order_mdl = self.order_mdl
        sap_order_addr_mdl = self.order_addrs_mdl
        sap_bsns_partner_mdl = self.bsns_partner_mdl
        sap_bsns_partner_contact_mdl = self.bsns_partner_contact_mdl
        user_obj = User.objects.get(username=APP_USERNAME)
        orders = self.search_all(from_date=from_date)

        for order in orders:
            # Extraction of order information
            ordr_info = order[sap_order_mdl]
            doc_num = str(ordr_info['DocNum'])
            ccy_code = str(ordr_info['DocCurrency'])
            web_ordr_ref = ordr_info['U_WedDocNum']
            sale_channel_code = str(ordr_info['U_TipoVenta'])
            seller_code = str(ordr_info['SalesPersonCode'])
            create_date = ordr_info['DocDate']
            tax_date = ordr_info['TaxDate']
            commit_date = ordr_info['DocDueDate']
            local_total_amt = ordr_info['DocTotal']
            sys_total_amt = ordr_info['DocTotalSys']
            local_total_tax = ordr_info['VatSum']
            sys_total_tax = ordr_info['VatSumSys']
            total_dcnt = ordr_info['TotalDiscount']
            status = ordr_info['DocumentStatus']
            cancel_status = ordr_info['Cancelled']

            # Extraction of order address information
            ordr_addr_info = order[sap_order_addr_mdl]
            ordr_bill_addr_ref = ordr_info['PayToCode']
            ordr_bill_st_and_num = ordr_addr_info['BillToStreet']
            ordr_bill_muni_name = ordr_addr_info['BillToCounty']
            ordr_ship_addr_ref = ordr_info['ShipToCode']
            ordr_ship_st_and_num = ordr_addr_info['ShipToStreet']
            ordr_ship_muni_name = ordr_addr_info['ShipToCounty']

            # Extraction of business partner information
            bsns_partner_info = order[sap_bsns_partner_mdl]
            bsns_partner_code = bsns_partner_info['CardCode']
            bsns_partner_name = bsns_partner_info['CardName']
            bsns_partner_ccy_code = str(bsns_partner_info['Currency'])
            bsns_partner_group_code = str(bsns_partner_info['GroupCode'])
            bsns_partner_tax_id = bsns_partner_info['FederalTaxID']
            bsns_partner_type_code = str(bsns_partner_info['CardType'])
            bsns_partner_phone1 = bsns_partner_info['Phone1']
            bsns_partner_phone2 = bsns_partner_info['Phone2']
            bsns_partner_email_addr = bsns_partner_info['EmailAddress']

            # Extraction of business partner contact information
            contact_info = order[sap_bsns_partner_contact_mdl]
            contact_code = str(ordr_info['ContactPersonCode'])
            contact_ref = contact_info['Name']
            contact_first_name = contact_info['FirstName'] or ''
            contact_middle_name = contact_info['MiddleName'] or ''
            contact_last_name = contact_info['LastName'] or ''
            contact_phone1 = contact_info['Phone1']
            contact_phone2 = contact_info['Phone2']
            contact_mobile_phone = contact_info['MobilePhone']
            contact_email_addr = contact_info['E_Mail']
            contact_st_and_num = contact_info['Address'] or ''

            # validations start
            # ----------------------------------------------------------------
            # validation of currency existence (by code) in model
            try:
                ccy = ccy_mdl.objects.get(code=ccy_code,
                                          service_acct=self.serv_account,)
            except ccy_mdl.DoesNotExist:
                e_msg = f'Error: currency code \'{ccy_code}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of existence of equivalence for SAP currency
            ccy = ccy.currency
            if not ccy:
                e_msg = 'Error: currency code '
                e_msg += f'\'{ccy_code}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # Equals the currency object
            if ccy_code == bsns_partner_ccy_code:
                bsns_partner_ccy = ccy
            else:
                # validation of bsns partner currency existence (by code) in model
                try:
                    bsns_partner_ccy = (ccy_mdl.objects
                                        .get(code=bsns_partner_ccy_code,
                                             service_acct=self.serv_account))
                except ccy_mdl.DoesNotExist:
                    e_msg = 'Error: bsns partner currency code '
                    e_msg += f'\'{bsns_partner_ccy_code}\' does not exist'
                    e_msg += f'\nOrder: {doc_num}'
                    CustomError(msg=e_msg)
                    continue

                # validation of existence of equivalence for SAP currency
                bsns_partner_ccy = bsns_partner_ccy.currency
                if not ccy:
                    e_msg = 'Error: bsns partner currency code '
                    e_msg += f'\'{bsns_partner_ccy_code}\' has no equivalence'
                    e_msg += f'\nOrder: {doc_num}'
                    CustomError(msg=e_msg)
                    continue

            # validation of sale channel existence (by code) in model
            try:
                sale_channel = (sale_channel_mdl.objects
                                .get(code=sale_channel_code,
                                     service_acct=self.serv_account))
            except sale_channel_mdl.DoesNotExist:
                e_msg = 'Error: sale channel code '
                e_msg += f'\'{sale_channel_code}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of existence of equivalence for SAP sale channel
            sale_channel = sale_channel.sale_channel
            if not sale_channel:
                e_msg = 'Error: sale channel code '
                e_msg += f'\'{sale_channel_code}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of seller existence (by code) in model
            try:
                seller = employee_mdl.objects.get(code=seller_code,
                                                  service_acct=self.serv_account)
            except employee_mdl.DoesNotExist:
                e_msg = f'Error: seller code \'{seller_code}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of existence of equivalence for SAP seller
            seller = seller.employee
            if not seller:
                e_msg = 'Error: seller code '
                e_msg += f'\'{seller_code}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of order bill muni existence (by name) in model
            try:
                ordr_bill_muni = muni_mdl.objects.get(name=ordr_bill_muni_name,
                                                      service_acct=self.serv_account)
            except muni_mdl.DoesNotExist:
                e_msg = 'Error: order bill muni name '
                e_msg += f'\'{ordr_bill_muni_name}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue
            except muni_mdl.MultipleObjectsReturned:
                ordr_bill_muni = (muni_mdl.objects
                                  .filter(name=ordr_bill_muni_name,
                                          service_acct=self.serv_account)
                                  .first())

            # validation of existence of equivalence for SAP muni
            ordr_bill_muni = ordr_bill_muni.muni
            if not ordr_bill_muni:
                e_msg = 'Error: order bill muni name '
                e_msg += f'\'{ordr_bill_muni_name}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # Equals the muni object
            if ordr_bill_muni_name == ordr_ship_muni_name:
                ordr_ship_muni = ordr_bill_muni
            else:
                # validation of order ship muni existence (by name) in model
                try:
                    ordr_ship_muni = (muni_mdl.objects
                                      .get(name=ordr_ship_muni_name,
                                           service_acct=self.serv_account))
                except muni_mdl.DoesNotExist:
                    e_msg = 'Error: order ship muni name '
                    e_msg += f'\'{ordr_ship_muni_name}\' does not exist'
                    e_msg += f'\nOrder: {doc_num}'
                    CustomError(msg=e_msg)
                    continue
                except muni_mdl.MultipleObjectsReturned:
                    ordr_ship_muni = (muni_mdl.objects
                                      .filter(name=ordr_ship_muni_name,
                                              service_acct=self.serv_account)
                                      .first())

                # validation of existence of equivalence for SAP muni
                ordr_ship_muni = ordr_ship_muni.muni
                if not ordr_ship_muni:
                    e_msg = 'Error: order ship muni name '
                    e_msg += f'\'{ordr_ship_muni_name}\' has no equivalence'
                    e_msg += f'\nOrder: {doc_num}'
                    CustomError(msg=e_msg)
                    continue

            # validation of bsns partner group existence (by name) in model
            try:
                bsns_partner_group = (group_mdl.objects
                                      .get(code=bsns_partner_group_code,
                                           service_acct=self.serv_account))
            except group_mdl.DoesNotExist:
                e_msg = 'Error: bsns partner group code '
                e_msg += f'\'{bsns_partner_group_code}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of existence of equivalence for SAP bsns partner group
            bsns_partner_group = bsns_partner_group.group
            if not bsns_partner_group:
                e_msg = 'Error: bsns partner group code '
                e_msg += f'\'{bsns_partner_group_code}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of bsns partner type existence (by name) in model
            try:
                bsns_partner_type = (type_mdl.objects
                                     .get(code=bsns_partner_type_code,
                                          service_acct=self.serv_account))
            except type_mdl.DoesNotExist:
                e_msg = 'Error: bsns partner type code '
                e_msg += f'\'{bsns_partner_type_code}\' does not exist'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue

            # validation of existence of equivalence for SAP bsns partner type
            bsns_partner_type = bsns_partner_type.type
            if not bsns_partner_type:
                e_msg = 'Error: bsns partner type code '
                e_msg += f'\'{bsns_partner_type_code}\' has no equivalence'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg)
                continue
            # ----------------------------------------------------------------
            # validations end

            sync_kwargs = {'model': mdl}
            addr_sync_kwargs = {'model': addr_mdl}
            contact_addr_sync_kwargs = {'model': addr_mdl}
            bsns_partner_sync_kwargs = {'model': bsns_partner_mdl}
            contact_sync_kwargs = {'model': contact_mdl}
            try:
                bsns_partner = (bsns_partner_mdl.objects
                                .get(code=bsns_partner_code))
                bsns_partner_sync_func = bulk_update_with_history
                bsns_partner_sync_kwargs['fields'] = [
                    'name',
                    'currency',
                    'group',
                    'tax_id',
                    'type',
                    'phone1',
                    'phone2',
                    'email_addr',
                    'changed_by',
                ]
            except bsns_partner_mdl.DoesNotExist:
                bsns_partner = bsns_partner_mdl()
                bsns_partner.code = bsns_partner_code
                bsns_partner_sync_func = bulk_create_with_history
            try:
                contact = contact_mdl.objects.get(code=contact_code)
                contact_sync_func = bulk_update_with_history
                contact_sync_kwargs['fields'] = [
                    'reference',
                    'first_name',
                    'last_name',
                    'addr',
                    'phone1',
                    'phone2',
                    'mobile_phone',
                    'email_addr',
                    'changed_by',
                ]

                contact_addr = contact.addr
                contact_addr_sync_kwargs['fields'] = [
                    'reference',
                    'st_and_num',
                    'muni',
                    'changed_by',
                ]
            except contact_mdl.DoesNotExist:
                contact = contact_mdl()
                contact.code = contact_code

                contact_addr = addr_mdl()

                contact_sync_func = bulk_create_with_history
            try:
                ordr = (mdl.objects.select_related('ship_addr',
                                                   'bill_addr')
                        .get(doc_num=doc_num, service_acct=self.serv_account))
                ordr_ship_addr = ordr.ship_addr
                ordr_bill_addr = ordr.bill_addr

                sync_func = bulk_update_with_history
                sync_kwargs['fields'] = [
                    'reference',
                    'service_acct',
                    'currency',
                    'web_order_ref',
                    'sale_channel',
                    'seller',
                    'create_date',
                    'tax_date',
                    'commit_date',
                    'ship_addr',
                    'bill_addr',
                    'contact',
                    'local_total_dcnt',
                    'doc_total_dcnt',
                    'local_total_tax',
                    'doc_total_tax',
                    'local_total_amt',
                    'doc_total_amt',
                    'enabled',
                    'changed_by',
                ]
                addr_sync_kwargs['fields'] = [
                    'reference',
                    'st_and_num',
                    'muni',
                    'changed_by',
                ]
            except mdl.DoesNotExist:
                ordr = mdl()
                ordr.doc_num = doc_num
                ordr_ship_addr = addr_mdl()
                ordr_bill_addr = addr_mdl()

                sync_func = bulk_create_with_history

            contact_addr.st_and_num = contact_st_and_num
            contact_addr.muni = None
            contact_addr.changed_by = user_obj
            contact_addr_sync_kwargs['objs'] = [contact_addr]
            try:
                contact_addr_sync = contact_sync_func(
                    **contact_addr_sync_kwargs)
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue
            contact_addr = (contact_addr_sync[0]
                            if contact_addr_sync
                            else contact_addr)

            contact.reference = contact_ref
            contact.first_name = ' '.join([
                contact_first_name,
                contact_middle_name
            ])
            contact.last_name = contact_last_name
            contact.phone1 = contact_phone1
            contact.phone2 = contact_phone2
            contact.mobile_phone = contact_mobile_phone
            contact.email_addr = contact_email_addr
            contact.addr = contact_addr
            contact.changed_by = user_obj
            contact_sync_kwargs['objs'] = [contact]
            try:
                contact_sync = contact_sync_func(**contact_sync_kwargs)
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue
            contact = contact_sync[0] if contact_sync else contact

            ordr_ship_addr.reference = ordr_ship_addr_ref
            ordr_ship_addr.st_and_num = ordr_ship_st_and_num
            ordr_ship_addr.muni = ordr_ship_muni
            ordr_ship_addr.changed_by = user_obj
            addr_sync_kwargs['objs'] = [ordr_ship_addr]
            try:
                ordr_ship_addr_sync = sync_func(**addr_sync_kwargs)
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue

            ordr_ship_addr = (ordr_ship_addr_sync[0]
                              if ordr_ship_addr_sync
                              else ordr_ship_addr)

            ordr_bill_addr.reference = ordr_bill_addr_ref
            ordr_bill_addr.st_and_num = ordr_bill_st_and_num
            ordr_bill_addr.muni = ordr_bill_muni
            ordr_bill_addr.changed_by = user_obj
            addr_sync_kwargs['objs'] = [ordr_bill_addr]
            try:
                ordr_bill_addr_sync = sync_func(**addr_sync_kwargs)
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue
            ordr_bill_addr = (ordr_bill_addr_sync[0]
                              if ordr_bill_addr_sync
                              else ordr_bill_addr)

            bsns_partner.name = bsns_partner_name
            bsns_partner.currency = bsns_partner_ccy
            bsns_partner.group = bsns_partner_group
            bsns_partner.tax_id = bsns_partner_tax_id
            bsns_partner.type = bsns_partner_type
            bsns_partner.phone1 = bsns_partner_phone1
            bsns_partner.phone2 = bsns_partner_phone2
            bsns_partner.email_addr = bsns_partner_email_addr
            bsns_partner.changed_by = user_obj
            bsns_partner_sync_kwargs['objs'] = [bsns_partner]
            try:
                bsns_partner_sync = bsns_partner_sync_func(
                    **bsns_partner_sync_kwargs
                )
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue
            bsns_partner = (bsns_partner_sync[0]
                            if bsns_partner_sync
                            else bsns_partner)

            ordr.reference = f'{self.serv_account.reference}{doc_num}'
            ordr.service_acct = self.serv_account
            ordr.currency = ccy
            ordr.web_order_ref = web_ordr_ref
            ordr.sale_channel = sale_channel
            ordr.seller = seller
            ordr.create_date = create_date
            ordr.tax_date = tax_date
            ordr.commit_date = commit_date
            ordr.updtd_commit_date = commit_date
            ordr.ship_addr = ordr_ship_addr
            ordr.bill_addr = ordr_bill_addr
            ordr.customer = bsns_partner
            ordr.contact = contact
            ordr.local_total_dcnt = total_dcnt
            ordr.doc_total_dcnt = total_dcnt
            ordr.local_total_tax = local_total_tax
            ordr.doc_total_tax = sys_total_tax
            ordr.local_total_amt = local_total_amt
            ordr.doc_total_amt = sys_total_amt
            ordr.enabled = cancel_status == 'tNO' and status == 'O'
            ordr.changed_by = user_obj
            sync_kwargs['objs'] = [ordr]
            try:
                ordr_sync = sync_func(**sync_kwargs)
            except Exception:
                tb = traceback.format_exc()
                tb += f'\nOrder: {doc_num}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nOrder: {doc_num}'
                CustomError(msg=e_msg, log=tb)
                continue
            ordr = ordr_sync[0] if ordr_sync else ordr
