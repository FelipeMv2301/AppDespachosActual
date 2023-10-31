import os

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Case, F, Value, When
from django.shortcuts import render
from django.views.generic.base import View

from module.delivery.models.delivery import Delivery
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PUBLIC_HOSTS


class TrackView(View):
    template = os.path.join('delivery', 'track.html')
    allowed_domains = ALLOWED_PUBLIC_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @loggable
    def get(self,
            request: WSGIRequest,
            company_code: str,
            folio: str,
            *args,
            **kwargs):
        delivery = (Delivery.objects
                    .select_related(
                        'service_status',
                        'service_acct__company'
                    )
                    .filter(folio=folio, service_acct__service__code='STK')
                    .values(
                        'folio',
                        'issue_date',
                        'rcpt_commit_date',
                        'packages_qty',
                        serv_status_name=Case(
                            When(service_status__name__isnull=True,
                                 then=Value('No hay información')),
                            default='service_status__name'
                        ),
                        company_code=F('service_acct__company__code'),
                        company_trade_name=F('service_acct__company__trade_name'),)
                    .first())
        context = {'deliv': delivery,
                   'folio': folio,
                   'company_code': company_code}
        if not delivery:
            messages.error(request=request,
                           message='Orden de transporte no encontrada')

        return render(request=request,
                      template_name=self.template,
                      context=context)
