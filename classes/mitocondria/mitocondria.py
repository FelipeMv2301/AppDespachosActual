import os
import traceback
from pathlib import Path
from typing import Callable

import MySQLdb as mysql

from core.settings.base import env
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError

CURRENT_DIR = Path(__file__).resolve().parent


class Mitocondria:
    def __init__(self, *args, **kwargs):
        # Mitocondria's database data
        self.schema = env.str(var='MITOCONDRIA_DB_SCHEMA')
        self.conn = None

        # Mitocondria's database models data
        self.disp_mdl = 'ad_despachos'
        self.disp_order_mdl = 'ad_despacho_pedido'
        self.order_mdl = 'ad_pedido'
        self.order_details_mdl = 'ad_pedido_detalle'
        self.order_order_details_mdl = 'ad_pedido_pedidos_detalles'
        self.muni_mdl = 'sys_comunas'
        self.ship_type_mdl = 'ad_despachos_param_tipo_entrega'
        self.ship_pay_type_mdl = 'ad_despachos_param_tipo_pago'

        # Mitocondria's database queries data
        self.queries_folder_path = os.path.join(CURRENT_DIR, 'sql')

        # Mitocondria object equivalences
        self.doc_types_equiv_by_code = {
            26: '33',  # Factura electrónica
            27: '52',  # Guía de despacho electrónica
            28: '39',  # Boleta electrónica
        }
        self.deliv_types_equiv_by_code = {
            1: 'RAG',  # Starken agencia
            2: 'ADOM',  # Starken domicilio
            3: 'RBQ',  # Bioquimica.cl
        }
        self.pay_types_equiv_by_code = {
            1: 'FREE',  # Retira en Bioquimica.cl
            2: 'CE',  # Cobrado en cotización
            3: 'PA',  # Paga contra entrega
        }

    @staticmethod
    def conn_handling(f: Callable):
        def wrapper(_self, *args, **kwargs):
            try:
                _self.connect()
                result = f(_self, *args, **kwargs)
                _self.disconnect()

                return result

            except Exception:
                tb = traceback.format_exc()
                e = CustomError(log=tb)
                raise e

        return wrapper

    @loggable
    def connect(self, *args, **kwargs) -> object:
        conn = mysql.connect(
            host=env.str(var='MITOCONDRIA_DB_HOST'),
            port=env.int(var='MITOCONDRIA_DB_PORT'),
            user=env.str(var='MITOCONDRIA_DB_USER'),
            passwd=env.str(var='MITOCONDRIA_DB_PASS'),
            db=self.schema
        )
        # TODO: check connection
        self.conn = conn

        return conn

    @loggable
    def disconnect(self, *args, **kwargs):
        self.conn.close()
