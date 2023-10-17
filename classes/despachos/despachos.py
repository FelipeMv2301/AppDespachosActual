import os
import traceback
from pathlib import Path
from typing import Callable

import MySQLdb as mysql

from app.general.models.service_account import ServiceAccount
from config.settings.base import env
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError

CURRENT_DIR = Path(__file__).resolve().parent
SERV_CODE = 'DESP'


class Despachos:
    def __init__(self, account: ServiceAccount, *args, **kwargs):
        # Despachos service account info
        self.serv_code = SERV_CODE
        self.serv_account = account

        # Despachos database data
        self.schema = env.str(var='DESPACHOS_DB_SCHEMA')
        self.conn = None

        # Despachos database queries data
        self.queries_folder_path = os.path.join(CURRENT_DIR, 'sql')

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
                e = CustomError(log=tb, notify=True)
                raise e

        return wrapper

    @loggable
    def connect(self, *args, **kwargs) -> object:
        conn = mysql.connect(
            host=self.serv_account.host,
            port=int(self.serv_account.port),
            user=self.serv_account.username,
            passwd=self.serv_account.get_password(),
            db=self.schema
        )
        # TODO: check connection
        self.conn = conn

        return conn

    @loggable
    def disconnect(self, *args, **kwargs):
        self.conn.close()
