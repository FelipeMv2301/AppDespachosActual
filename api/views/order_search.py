from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic.base import View

from app.order.models.order import Order
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS


class OrderSearchView(View):
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        doc_number_start = params.get('doc_num_start')
        if len(doc_number_start) <= 5:
            return HttpResponseNotFound()

        found_orders = (Order.objects.filter(
                doc_num__startswith=doc_number_start))

        if not found_orders:
            return HttpResponseNotFound()

        orders_data = [{
            'id': o.id,
            'doc_num': o.doc_num
        } for o in found_orders]

        return JsonResponse(data={'orders': orders_data})
