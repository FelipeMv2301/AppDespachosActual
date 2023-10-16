import os
from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic.base import View

from app.delivery.forms.kpis import DateRangeForm
from app.delivery.statistics.completion import Completion
from app.delivery.statistics.lead_times import LeadTimes
from app.delivery.statistics.ship_by_state import ShipByState
from config.settings.base import ALLOWED_PRIVATE_HOSTS
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable

PAGE_TITLE = 'Indicadores de Rendimiento'


class KpisView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'kpis.html')
    full_screen_template = os.path.join('delivery', 'kpis_full_screen.html')
    form = DateRangeForm
    permission_required = ('delivery.view_kpis')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        context = {'page_title': PAGE_TITLE,
                   'form': self.form()}

        today = date.today()
        date_fmt = '%Y-%m-%d'
        start_date = (datetime.strptime(params.get('start_date'), date_fmt)
                      if params.get('start_date')
                      else
                      today + timedelta(days=-30))
        end_date = (datetime.strptime(params.get('end_date'), date_fmt)
                    if params.get('end_date')
                    else
                    today)

        ship_by_region = ShipByState(start_date=start_date, end_date=end_date)
        if params.get('export_ship_by_state') is not None:
            return ship_by_region.export()
        elif params.get('line_graph_of_ship_by_state') is not None:
            display_type = 'line'
        else:
            display_type = 'choropleth_map'
        ship_by_region_graph = ship_by_region.graph(option=display_type)
        context['ship_by_state_graph'] = ship_by_region_graph.to_html()

        lead_times = LeadTimes(start_date=start_date, end_date=end_date)
        if params.get('export_lead_times') is not None:
            return lead_times.export()
        elif params.get('lead_times_ranges') is not None:
            display_type = 'ranges'
        else:
            display_type = 'status'
        lead_times_graph = lead_times.graph(option=display_type)
        context['lead_times_graph'] = lead_times_graph.to_html()

        completion = Completion(start_date=start_date, end_date=end_date)
        if params.get('export_completion') is not None:
            return completion.export()
        completion_graph = completion.graph()
        context['completion_graph'] = completion_graph.to_html()

        template = self.full_screen_template
        if params.get('show_ship_by_state') is not None:
            context['graph'] = ship_by_region_graph.to_html()
        elif params.get('show_lead_times') is not None:
            context['graph'] = lead_times_graph.to_html()
        elif params.get('show_completion') is not None:
            context['graph'] = completion_graph.to_html()
        else:
            template = self.template

        return render(request=request,
                      template_name=template,
                      context=context)
