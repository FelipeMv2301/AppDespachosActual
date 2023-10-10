import os
from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic.base import View
from app.delivery.statistics.ship_by_state import ShipByState

from app.delivery.forms.kpis import DateRangeForm
from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable

PAGE_TITLE = 'Indicadores de Rendimiento'


class KpisView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'kpis.html')
    form = DateRangeForm
    permission_required = ('delivery.view_kpis')

    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        params = request.GET
        print(params)
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

        return render(request=request,
                      template_name=self.template,
                      context=context)
