from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from module.delivery.models.opt import Option
from module.order.models.grouping import Grouping
from module.order.models.order import Order


class DeliveryFormView(APIView):
    permission_required = ('order.edit_all_order_delivery_form_from_api')
    allowed_domains = settings.ALLOWED_PRIVATE_HOSTS

    class Global:
        POST_PARAMS = {
            'order_refs': {
                'example_value': ['2305218', '2305217'],
                'type': list
            },
            'delivery_option_id': {
                'example_value': '2',
                'type': str
            }
        }

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def options(self, request: WSGIRequest | Request, *args, **kwargs):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)

        post_params = {}
        for key, val in self.Global.POST_PARAMS.items():
            post_params[key] = val['example_value']

        data['data'] = post_params
        return Response(data=data, status=HTTP_200_OK)

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def post(self, request: WSGIRequest | Request, *args, **kwargs):
        user = request.user
        params = request.POST

        response_msg = 'OK'
        response_status = HTTP_200_OK

        order_refs = set(params.getlist('order_refs'))
        deliv_opt_id = params.get('delivery_option_id')

        search_orders = Order.objects.filter(doc_num__in=order_refs)
        orders_found = {o.doc_num for o in search_orders}
        orders_not_found = order_refs.difference(orders_found)
        if orders_not_found:
            response_status = HTTP_404_NOT_FOUND
            response_msg = 'orders {ordrs} were not found'
            response_msg.format(ordrs=', '.join(orders_not_found))

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
