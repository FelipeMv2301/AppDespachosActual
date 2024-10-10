from django.conf import settings
from django.db.models import Count
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from api.permissions.edit_deliv_form_from_api import \
    EditDelivFormFromApiPermission
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from module.business_partner.models.bsns_partner import BusinessPartner
from module.business_partner.models.contact import Contact
from module.business_partner.models.group import Group
from module.business_partner.models.type import Type
from module.delivery.models.opt import Option
from module.general.models.address import Address
from module.general.models.currency import Currency
from module.general.models.employee import Employee
from module.general.models.muni import Muni
from module.general.models.service_account import ServiceAccount
from module.order.models.grouping import Grouping
from module.order.models.order import Order
from module.order.models.sale_channel import SaleChannel
from module.order.models.status import Status


class DeliveryFormView(APIView):
    permission_required = ('order.edit_all_order_delivery_form_from_api')
    allowed_domains = settings.ALLOWED_PRIVATE_HOSTS
    permission_classes = [IsAuthenticated, EditDelivFormFromApiPermission]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def post(self, request: Request, *args, **kwargs):
        user = request.user
        data = request.data

        response_msg = 'OK'
        response_status = HTTP_202_ACCEPTED

        order_ref = data.get('order_ref')
        if Order.objects.filter(doc_num=order_ref):
            return Response(status=response_status)

        # Creación de dirección de facturación
        bill_muni = Muni.objects.get(code=data.get('bill_muni_code'))
        bill_addr = Address.objects.create(
            st_and_num=data.get('bill_street_and_number'),
            complement=data.get('bill_complement'),
            muni=bill_muni,
            changed_by=user,
        )

        # Creación de dirección de entrega
        ship_muni = Muni.objects.get(code=data.get('ship_muni_code'))
        ship_addr = Address.objects.create(
            st_and_num=data.get('ship_street_and_number'),
            complement=data.get('ship_complement'),
            muni=ship_muni,
            changed_by=user,
        )

        # Creación o actualización de cliente
        currency = Currency.objects.get(code='CLP')
        tax_id = data.get('customer_tax_id')
        customer = BusinessPartner.objects.filter(tax_id=tax_id)
        if customer:
            customer.update(
                name=data.get('customer_name'),
                phone1=data.get('customer_phone1'),
                phone2=data.get('customer_phone2'),
                mobile_phone=data.get('customer_mobile_phone'),
                email_addr=data.get('customer_email_addr'),
                changed_by=user,
            )
            customer = customer.first()
        else:
            customer_group = Group.objects.get(code='CN')
            customer_type = Type.objects.get(code='CL')
            customer = BusinessPartner.objects.create(
                code=f'CN{tax_id}',
                name=data.get('customer_name'),
                currency=currency,
                group=customer_group,
                tax_id=tax_id,
                type=customer_type,
                phone1=data.get('customer_phone1'),
                phone2=data.get('customer_phone2'),
                mobile_phone=data.get('customer_mobile_phone'),
                email_addr=data.get('customer_email_addr'),
                changed_by=user,
            )

        # Creación de contacto
        contact = Contact.objects.create(
            first_name=data.get('contact_first_name'),
            last_name=data.get('contact_last_name'),
            addr=ship_addr,
            phone1=data.get('contact_phone1'),
            phone2=data.get('contact_phone2'),
            mobile_phone=data.get('contact_mobile_phone'),
            email_addr=data.get('contact_email_addr'),
            changed_by=user,
        )

        # Creación del pedido
        sale_channel = SaleChannel.objects.get(code='WEB')
        seller = Employee.objects.get(code='SAYB38')
        status = Status.objects.get(code='CLOSE')
        service_acct = ServiceAccount.objects.get(code='SAPBQ01')
        order = Order.objects.create(
            doc_num=order_ref,
            reference=order_ref,
            service_acct=service_acct,
            currency=currency,
            web_order_ref=order_ref,
            sale_channel=sale_channel,
            seller=seller,
            create_date=data.get('creation_date'),
            tax_date=data.get('tax_date'),
            commit_date=data.get('commit_date'),
            updtd_commit_date=data.get('commit_date'),
            ship_addr=ship_addr,
            bill_addr=bill_addr,
            customer=customer,
            contact=contact,
            local_total_dcnt=data.get('total_discount') or 0,
            doc_total_dcnt=data.get('total_discount') or 0,
            local_total_tax=data.get('local_total_tax') or 0,
            doc_total_tax=data.get('local_total_tax') or 0,
            local_total_amt=data.get('local_total_amt') or 0,
            doc_total_amt=data.get('local_total_amt') or 0,
            status=status,
            changed_by=user,
        )

        # Creación de la agrupación de pedido
        deliv_opt = Option.objects.get(id=data.get('delivery_option_id'))
        Grouping.objects.create(
            code=Grouping.new_code(),
            order=order,
            delivery_option=deliv_opt,
            addr=ship_addr,
            customer=customer,
            contact=contact,
            changed_by=user,
        )

        return Response(data={'message': response_msg}, status=response_status)

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def obsolete_post(self, request: Request, *args, **kwargs):
        user = request.user
        data = request.data

        response_msg = 'OK'
        response_status = HTTP_202_ACCEPTED

        order_refs = set(data.get('order_refs'))
        deliv_opt_id = data.get('delivery_option_id')

        search_orders = Order.objects.filter(doc_num__in=order_refs)
        orders_found = {o.doc_num for o in search_orders}
        orders_not_found = order_refs.difference(orders_found)
        if orders_not_found:
            response_status = HTTP_404_NOT_FOUND
            response_msg = ('orders {ordrs} were not found'
                            .format(ordrs=', '.join(orders_not_found)))

        search_deliv_opt = Option.objects.filter(id=deliv_opt_id).first()
        if not search_deliv_opt:
            response_status = HTTP_404_NOT_FOUND
            response_msg = f'ID {deliv_opt_id} delivery option not found'

        if response_status == HTTP_404_NOT_FOUND:
            return Response(data={'message': response_msg},
                            status=response_status)

        search_orders_group = Grouping.objects.filter(order__in=search_orders,
                                                      enabled=True)
        search_orders_group = (search_orders_group
                               .values('code')
                               .annotate(code_count=Count('code')))
        search_orders_group = (search_orders_group
                               .filter(code_count=len(search_orders)))

        group_sync_kwargs = {'model': Grouping}
        if search_orders_group:
            group_sync_func = bulk_update_with_history
            group_sync_kwargs['fields'] = ['delivery_option']

            orders_group_code = search_orders_group[0]['code']
            group = Grouping.objects.filter(code=orders_group_code)
            order_group_objs = group
        else:
            group_sync_func = bulk_create_with_history
            orders_group_code = Grouping.new_code()

            first_order = search_orders.first()
            order_contact = first_order.contact
            order_contact.id = None
            order_contact.code = order_contact.new_code()
            order_contact.save()

            order_addr = first_order.ship_addr
            order_addr.id = None
            order_addr.code = order_addr.new_code()
            order_addr.save()

            order_group_objs = [
                Grouping(
                    code=orders_group_code,
                    order=order,
                    addr=order_addr,
                    customer=first_order.customer,
                    contact=order_contact,
                ) for order in search_orders
            ]

        for group in order_group_objs:
            group.delivery_option = search_deliv_opt
            group.changed_by = user

        group_sync_kwargs['objs'] = order_group_objs
        group_sync_func(**group_sync_kwargs)

        return Response(data={'message': response_msg}, status=response_status)
