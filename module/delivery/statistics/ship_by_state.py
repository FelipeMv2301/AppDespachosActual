import json
import mimetypes
from datetime import date
from io import BytesIO
from typing import Dict, Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from django.shortcuts import HttpResponse

from module.delivery.models.delivery import Delivery
from module.delivery.statistics.delivery import Delivery as DelivStat
from module.general.models.state import State
from helpers import globals as gb


class ShipByState(DelivStat):
    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        super().__init__(start_date=start_date,
                         end_date=end_date,
                         *args,
                         **kwargs)
        self.states = {st.name: {'Cantidad': 0} for st in State.objects.all()}
        shipments = Delivery.query_for_stat(start_date=self.start_date,
                                            end_date=self.end_date)
        for shipment in shipments:
            state_name = shipment.state_name
            self.states[state_name]['Cantidad'] += 1

        if self.states:
            self.df = pd.DataFrame.from_dict([{
                    'Región': name,
                    'Cantidad': info['Cantidad'],
            } for name, info in self.states.items()]).sort_values('Región')
        else:
            self.df = pd.DataFrame.from_dict([{'Región': '', 'Cantidad': ''}])

    def __get_state_color_by_ship_qty(self) -> Dict[str, str]:
        colors = {}
        for name, info in self.states.items():
            qty = info['Cantidad']
            if qty >= 100:
                color = '#ed3833'
            elif qty >= 50:
                color = '#f3993e'
            elif qty >= 10:
                color = '#fce54d'
            elif qty == 0:
                color = '#ffffff'
            else:
                color = '#4a86e7'

            colors.setdefault(name, color)

        return colors

    def graph(self, option: Literal['choropleth_map', 'line']) -> go.Figure:
        title = (f'Presencialidad por región entre {self.start_date_str} y '
                 f'{self.end_date_str}')
        colors = self.__get_state_color_by_ship_qty()

        if option == 'line':
            fig = px.line(
                data_frame=self.df,
                x='Región',
                y='Cantidad',
                markers=True,
                title=title,
                text='Cantidad'
            )
            fig.update_traces(line_color='#4a86e7')
            fig.update_traces(textposition='bottom right')
            fig.update_layout(plot_bgcolor='#f7f7f7')
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#bdbfc1')
            fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='#6c757d')
        elif option == 'choropleth_map':
            cl_regions_geo = json.loads(s=open(file=gb.CL_REGIONS_GEOJSON_PATH,
                                               mode='r',
                                               encoding='utf-8',
                                               errors='ignore').read())

            fig = px.choropleth(
                data_frame=self.df,
                geojson=cl_regions_geo,
                locations='Región',
                featureidkey='properties.region_name_in_db',
                color='Región',
                color_discrete_map=colors,
                title=title,
                center={'lat': -35.995785, 'lon': -71.762696},
                hover_data=['Cantidad']
            )
            fig.update_layout(margin={'r': 40, 't': 40, 'l': 40, 'b': 40})
            fig.update_geos(fitbounds='locations', visible=False)
            fig.update_geos(bgcolor='rgba(0,0,0,0)')

        return fig

    def export(self) -> HttpResponse:
        filename = ('presencialidad_por_region_entre_'
                    f"{self.start_date_str}_{self.end_date_str}.xlsx")
        with BytesIO() as b:
            writer = pd.ExcelWriter(path=b, engine='xlsxwriter')
            self.df.to_excel(excel_writer=writer, index=False)
            writer.close()
            response = HttpResponse(
                b.getvalue(),
                content_type=mimetypes.guess_type(filename)[0]
            )
            response['Content-Disposition'] = ('attachment; '
                                               f"filename={filename}")
            return response
