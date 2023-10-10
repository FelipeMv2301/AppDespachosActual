from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic.base import View

from app.order.models.grouping import Grouping
from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable


class OrderGroupSearchView(View):
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        doc_num = str(params.get('doc_num'))
        code = params.get('code')

        if code:
            found_group = (
                Grouping.objects
                .filter(
                    code=code,
                    enabled=True
                )
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
                    contact_email_addr=F('contact__email_addr'),
                    obs=F('deliv_obs'),
                )
                .first()
            )
            if not found_group:
                return HttpResponseNotFound()

            data = {'group': found_group}
        elif doc_num and len(doc_num) > 5:
            found_orders = [
                obj
                for obj in Grouping.query_for_delivery_issue(ordr_doc_num=doc_num)
            ]

            if not found_orders:
                return HttpResponseNotFound()

            orders_data = [{
                'code': o.code,
                'doc_nums': o.doc_nums
            } for o in found_orders]

            data = {'orders': orders_data}
        else:
            return HttpResponseNotFound()

        return JsonResponse(data=data)
