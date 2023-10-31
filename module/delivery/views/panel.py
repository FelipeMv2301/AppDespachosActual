import os
from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View

from module.delivery.forms.panel import PanelForm
from module.order.models.delivery import OrderDelivery
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from project.settings.base import ALLOWED_PRIVATE_HOSTS

PAGE_TITLE = 'Panel de entregas'


class PanelView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'panel.html')
    form = PanelForm
    permission_required = ('delivery.view_delivery_panel')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request, *args, **kwargs):
        params = request.GET
        context = {'page_title': PAGE_TITLE, 'form': self.form()}

        status = params.get('status')
        carriers = params.get('carrier')
        updtd_commit_start_date = params.get('updtd_commit_start_date')
        updtd_commit_end_date = params.get('updtd_commit_end_date')
        issue_start_date = params.get('issue_start_date')
        issue_end_date = params.get('issue_end_date')

        date_fmt = '%Y-%m-%d'
        filters = {}
        if updtd_commit_start_date:
            try:
                updtd_commit_start_date = datetime.strptime(updtd_commit_start_date,
                                                            date_fmt).strftime(date_fmt)
                filters.update({
                    'order_grouping__order__updtd_commit_date__gte': updtd_commit_start_date
                })
            except Exception:
                pass
        if updtd_commit_end_date:
            try:
                updtd_commit_end_date = datetime.strptime(updtd_commit_end_date,
                                                          date_fmt).strftime(date_fmt)
                filters.update({
                    'order_grouping__order__updtd_commit_date__lte': updtd_commit_end_date
                })
            except Exception:
                pass
        if issue_start_date:
            try:
                issue_start_date = datetime.strptime(issue_start_date,
                                                     date_fmt).strftime(date_fmt)
                filters.update({
                    'delivery__issue_date__gte': issue_start_date
                })
            except Exception:
                pass
        if issue_end_date:
            try:
                issue_end_date = datetime.strptime(issue_end_date,
                                                   date_fmt).strftime(date_fmt)
                filters.update({
                    'delivery__issue_date__lte': issue_end_date
                })
            except Exception:
                pass
        if status:
            try:
                status = status.split(',')
                filters.update({
                    'delivery__status__code__in': status
                })
            except Exception:
                pass
        if carriers:
            try:
                carriers = carriers.split(',')
                filters.update({
                    'delivery__service_acct__service__code__in': carriers
                })
            except Exception:
                pass
        limit = 500
        od = (OrderDelivery.objects
              .select_related('delivery',
                              'delivery__status',
                              'delivery__service_acct__service',
                              'order_grouping__order')
              .filter(**filters)
              .order_by('delivery__id'))[:limit]
        delivs = []
        for o in od:
            folio = o.delivery.folio
            doc_num = o.order_grouping.order.doc_num
            deliv = {
                'doc_nums': doc_num,
                'updtd_commit_date': o.order_grouping.order.updtd_commit_date,
                'folio': folio,
                'carrier_name': o.delivery.service_acct.service.name,
                'assy_date': o.delivery.assembly_date,
                'issue_date': o.delivery.issue_date,
                'rcpt_commit_date': o.delivery.rcpt_commit_date,
                'rcpt_date': o.delivery.rcpt_date,
                'status_name': o.delivery.status.name,
            }
            delivs.append(deliv)

        html_table = ''
        for i, data in enumerate(iterable=delivs):
            html_table += (f'<tr><th scope="row">{i+1}</th>'
                           f'<td>{data["doc_nums"]}</td>'
                           f'<td>{data["updtd_commit_date"]}</td>'
                           f'<td>{data["folio"]}</td>'
                           f'<td>{data["carrier_name"]}</td>'
                           f'<td>{data["assy_date"]}</td>'
                           f'<td>{data["issue_date"] or "No existe"}</td>'
                           f'<td>{data["rcpt_commit_date"] or "No existe"}</td>'
                           f'<td>{data["rcpt_date"] or "No existe"}</td>'
                           f'<td>{data["status_name"]}</td></tr>')
        context['html_table'] = html_table

        return render(request=request,
                      template_name=self.template,
                      context=context)
