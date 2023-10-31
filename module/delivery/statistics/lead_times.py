import mimetypes
from datetime import date
from io import BytesIO
from typing import Literal

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from django.shortcuts import HttpResponse

from module.delivery.models.delivery import Delivery
from module.delivery.statistics.delivery import Delivery as DelivStat


class LeadTimes(DelivStat):
    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        super().__init__(start_date=start_date,
                         end_date=end_date,
                         *args,
                         **kwargs)
        self.status = {'En plazo': {'Cantidad': 0, 'Color': '#155394'},
                       'Atrasado': {'Cantidad': 0, 'Color': '#ed3833'}}
        self.ranges = {
            '4+ días antes': {'Cantidad': 0, 'Color': '#155394'},
            '1 a 3 días antes': {'Cantidad': 0, 'Color': '#3d85c6'},
            '0 días': {'Cantidad': 0, 'Color': '#6fa8dd'},
            '1 a 3 días después': {'Cantidad': 0, 'Color': '#e06666'},
            '4+ días después': {'Cantidad': 0, 'Color': '#ed3833'}
        }
        self.shipments = Delivery.query_for_stat(start_date=self.start_date,
                                                 end_date=self.end_date)

    def graph(self, option: Literal['status', 'ranges']) -> go.Figure:
        if option == 'status':
            title = 'Estados '
            data = self.status
        elif option == 'ranges':
            title = 'Rangos '
            data = self.ranges
        title += (f'de entregas entre {self.start_date_str} y '
                  f'{self.end_date_str}')

        for ship in self.shipments:
            updtd_commit_date = ship.ordr_updtd_commit_date
            issue_date = ship.issue_date
            bsns_days_diff = np.busday_count(begindates=updtd_commit_date,
                                             enddates=issue_date)
            if option == 'status':
                if bsns_days_diff > 0:
                    key = 'Atrasado'
                else:
                    key = 'En plazo'
            elif option == 'ranges':
                if bsns_days_diff == 0:
                    key = '0 días'
                elif bsns_days_diff >= 4:
                    key = '4+ días después'
                elif bsns_days_diff <= -4:
                    key = '4+ días antes'
                elif 1 <= bsns_days_diff <= 3:
                    key = '1 a 3 días después'
                elif -1 >= bsns_days_diff >= -3:
                    key = '1 a 3 días antes'
            data[key]['Cantidad'] += 1

        df = pd.DataFrame.from_dict([
            {
                'Estado': stat_name,
                'Cantidad': stat_info['Cantidad'],
                'Color': stat_info['Color'],
            } for stat_name, stat_info in data.items()
        ])
        colors = {stat_name: stat_info['Color']
                  for stat_name, stat_info in data.items()}

        fig = px.pie(
            data_frame=df,
            values='Cantidad',
            names='Estado',
            color='Estado',
            color_discrete_map=colors,
            title=title
        )
        fig.update_traces(sort=False)

        return fig

    def export(self) -> HttpResponse:
        data = []
        for ship in self.shipments:
            commit_date = ship.ordr_updtd_commit_date
            issue_date = ship.issue_date
            bsns_days_diff = np.busday_count(begindates=commit_date,
                                             enddates=issue_date)
            if bsns_days_diff == 0:
                status = 'En plazo'
                range = '0 días'
            elif bsns_days_diff >= 4:
                status = 'Atrasado'
                range = '4+ días después'
            elif bsns_days_diff <= -4:
                status = 'En plazo'
                range = '4+ días antes'
            elif 1 <= bsns_days_diff <= 3:
                status = 'Atrasado'
                range = '1 a 3 días después'
            elif -1 >= bsns_days_diff >= -3:
                status = 'En plazo'
                range = '1 a 3 días antes'

            data.append({
                'Referencia pedido SAP': ship.doc_num,
                'Fecha creación pedido SAP': ship.ordr_create_date,
                'Fecha compromiso pedido SAP': ship.ordr_commit_date,
                'Fecha compromiso actualizada': ship.ordr_updtd_commit_date,
                'Observaciones pedido': ship.ordr_obs,
                'Referencia pedido web': ship.web_ordr_ref,
                'Orden de entrega': ship.folio,
                'Fecha armado': ship.assy_date,
                'Fecha emisión': ship.issue_date,
                'Fecha recepción cliente': ship.rcpt_date,
                'Desde Mitocondria': ship.from_mito,
                'Estado entrega': ship.status_name,
                'Estado externo despacho': ship.status_serv_name,
                'Tipo entrega': ship.deliv_type_name,
                'Vía entrega': ship.service_name,
                'Comuna entrega': ship.muni_name,
                'Región entrega': ship.state_name,
                'Rango de tiempo de entrega': range,
                'Estado de tiempo de entrega': status,
                'Observaciones entrega': ship.deliv_obs,
            })

        df = pd.DataFrame.from_dict(data or [{'': ''}])
        filename = ('tiempos_entrega_entre_'
                    f"{self.start_date_str}_{self.end_date_str}.xlsx")
        with BytesIO() as b:
            writer = pd.ExcelWriter(path=b, engine='xlsxwriter')
            df.to_excel(excel_writer=writer, index=False)
            writer.close()
            response = HttpResponse(
                b.getvalue(),
                content_type=mimetypes.guess_type(filename)[0]
            )
            response['Content-Disposition'] = ('attachment; '
                                               f"filename={filename}")
            return response
