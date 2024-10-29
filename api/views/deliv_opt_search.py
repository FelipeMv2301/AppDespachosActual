from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Case, CharField, F, Q, Value, When
from django.db.models.functions import Concat
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic.base import View

from module.delivery.models.opt import Option
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS


class DelivOptSearchView(View):
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        carrier_code = params.get('carrier')
        muni_code = params.get('delivMuni')
        type_code = params.get('delivType')

        service_filter = Q(carrier__code=carrier_code)
        enabled_filter = (Q(enabled=True) &
                          Q(carrier__serviceaccount_enabled=True))
        filter_for_branch = (Q(branch__addr__muni__code=muni_code) &
                             Q(branch__delivery=True) &
                             Q(branch__enabled=True) &
                             Q(type__code=type_code))

        found_opts = (Option.objects
                      .filter(service_filter & enabled_filter)
                      .values(carrier_code=F('carrier__code'),
                              carrier_name=F('carrier__name'),
                              service_code=F('service__code'),
                              service_name=F('service__name'),
                              type_code=F('type__code'),
                              type_name=F('type__name'),
                              pay_type_code=F('pay_type__code'),
                              pay_type_name=F('pay_type__name'),
                              branch_code=Case(
                                    When(filter_for_branch,
                                         then=F('branch__code')),
                                    default=None,
                                    output_field=CharField()
                              ),
                              branch_name=Case(
                                    When(filter_for_branch,
                                         then=Concat('branch__name',
                                                     Value(' - '),
                                                     'branch__addr__st_and_num')),
                                    default=None,
                                    output_field=CharField()
                              ),
                              branch_deliv=F('branch__delivery'),
                              muni_code=F('branch__addr__muni__code'),
                              acct_code=F('carrier__serviceaccount__code'),
                              acct_name=Concat('carrier__serviceaccount__name',
                                               Value(' - '),
                                               'carrier__serviceaccount__desc')))

        if not found_opts:
            return HttpResponseNotFound()

        opts_data = [{
            'id': o.get('id'),
            'carrier_code': o.get('carrier_code'),
            'carrier_name': o.get('carrier_name'),
            'service_code': o.get('service_code'),
            'service_name': o.get('service_name'),
            'type_code': o.get('type_code'),
            'type_name': o.get('type_name'),
            'pay_type_code': o.get('pay_type_code'),
            'pay_type_name': o.get('pay_type_name'),
            'branch_code': o.get('branch_code'),
            'branch_name': o.get('branch_name'),
            'acct_code': o.get('acct_code'),
            'acct_name': o.get('acct_name'),
        } for o in found_opts]

        return JsonResponse(data={'opts': opts_data})
