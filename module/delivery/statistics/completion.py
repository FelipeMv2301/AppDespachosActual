import mimetypes
from datetime import date
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from django.shortcuts import HttpResponse

from module.delivery.models.delivery import Delivery
from module.delivery.statistics.delivery import Delivery as DelivStat


class Completion(DelivStat):
    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        super().__init__(start_date=start_date,
                         end_date=end_date,
                         *args,
                         **kwargs)
        self.status = {'Completo': {'Cantidad': 0, 'Color': '#38761d'},
                       'Con pendientes': {'Cantidad': 0, 'Color': '#ea4335'}}
        self.shipments = Delivery.query_for_stat(start_date=self.start_date,
                                                 end_date=self.end_date)

    def graph(self) -> go.Figure:
        title = (f'Tipo de entregas entre {self.start_date_str} y '
                 f'{self.end_date_str}')

        data = self.status
        for ship in self.shipments:
            is_complete = ship.is_complete
            key = 'Completo' if is_complete else 'Con pendientes'
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
            is_complete = ship.is_complete
            status = 'Completo' if is_complete else 'Con pendientes'

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
                'Tipo de envío de entrega': status,
                'Observaciones entrega': ship.deliv_obs,
            })

        df = pd.DataFrame.from_dict(data or [{'': ''}])
        filename = ('tipo_entrega_entre_'
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
