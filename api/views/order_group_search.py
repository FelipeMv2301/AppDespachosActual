from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, F
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic.base import View

from app.order.models.grouping import Grouping
from app.order.models.order import Order
from config.settings.base import ALLOWED_PRIVATE_HOSTS
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable


class OrderGroupSearchView(View):
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        doc_num = str(params.get('doc_num'))
        code = params.get('code')
        for_deliv_form = params.get('for_deliv_form')

        if doc_num and len(doc_num) > 5 and not code:
            found_orders = [
                obj
                for obj in Grouping.query_for_delivery_issue(ordr_doc_num=doc_num)
            ]

            if not found_orders:
                if not for_deliv_form:
                    return HttpResponseNotFound()
                ordr = (Order.objects
                        .select_related('contact',
                                        'ship_addr',
                                        'ship_addr__muni')
                        .filter(doc_num=doc_num).first())
                orders_data = {
                    'updtd_commit_date': ordr.updtd_commit_date,
                    'contact_first_name': ordr.contact.first_name,
                    'contact_last_name': ordr.contact.last_name,
                    'contact_email_addr': ordr.contact.email_addr,
                    'contact_mobile_phone': ordr.contact.mobile_phone,
                    'contact_phone1': ordr.contact.phone1,
                    'contact_phone2': ordr.contact.phone2,
                    'addr_st_and_num': ordr.ship_addr.st_and_num,
                    'addr_complement': ordr.ship_addr.complement,
                    'muni_code': ordr.ship_addr.muni.code,
                }
            else:
                group_data = (
                    Grouping.objects
                    .filter(id__in=[obj.id for obj in found_orders])
                    .values('code', 'id', c=Count('code'))
                )
                group_data = {d['id']: d['code'] for d in group_data}
                found_orders = [{'code': group_data[o.id],
                                 'doc_nums': o.doc_nums}
                                for o in found_orders]
                if not for_deliv_form:
                    orders_data = [{
                        'code': o['code'],
                        'doc_nums': o['doc_nums']
                    } for o in found_orders]
                else:
                    first_found_ordr = found_orders[0]
                    code = first_found_ordr['code']
                    orders_data = []

            data = {'orders': orders_data}
        if code:
            found_group = (
                Grouping.objects
                .filter(code=code)
                .select_related(
                    'delivery_option',
                    'delivery_option__service',
                    'delivery_option__carrier',
                    'delivery_option__branch',
                    'delivery_option__type',
                    'delivery_option__pay_type',
                    'addr',
                    'addr__muni',
                    'contact',
                    'order',
                )
                .values(
                    'enabled',
                    service_code=F('delivery_option__service__code'),
                    carrier_code=F('delivery_option__carrier__code'),
                    branch_code=F('delivery_option__branch__code'),
                    type_code=F('delivery_option__type__code'),
                    pay_type_code=F('delivery_option__pay_type__code'),
                    addr_st_and_num=F('addr__st_and_num'),
                    addr_complement=F('addr__complement'),
                    muni_code=F('addr__muni__code'),
                    contact_first_name=F('contact__first_name'),
                    contact_last_name=F('contact__last_name'),
                    contact_mobile_phone=F('contact__mobile_phone'),
                    contact_phone1=F('contact__phone1'),
                    contact_phone2=F('contact__phone2'),
                    contact_email_addr=F('contact__email_addr'),
                    obs=F('deliv_obs'),
                    updtd_commit_date=F('order__updtd_commit_date'),
                )
                .first()
            )
            if not found_group:
                return HttpResponseNotFound()

            data = {'group': found_group}

        return JsonResponse(data=data)
