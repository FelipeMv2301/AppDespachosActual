from datetime import date

import pandas as pd


class Delivery:
    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_str = start_date.strftime('%d-%m-%Y')
        self.end_date_str = end_date.strftime('%d-%m-%Y')

        self.base_df = pd.DataFrame.from_dict([{
                'Pedido SAP': '',
                'Fecha creación pedido SAP': '',
                'Fecha compromiso pedidos SAP': '',
                'Comuna cliente pedido SAP': '',
                'Observaciones pedido': '',
                'Pedido web': '',
                'Folio despacho': '',
                'Fecha despacho': '',
                'Via despacho': '',
                'Comuna Despacho': '',
                'Fecha recepción despacho': '',
                'Desde Mitocondria': '',
                'Desde App': '',
                'Observaciones despacho': ''
        }])
        self.color_base_info = {}

    # @staticmethod
    # def date_to_str(date: datetime | date) -> str:
    #     return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
