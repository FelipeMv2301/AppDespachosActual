import os
from typing import Dict, List

from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.general.models.muni_mito import MuniMito
from classes.mitocondria.mitocondria import Mitocondria
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable


class Municipality(Mitocondria):
    def __init__(self,
                 code: int | str = None,
                 name: str = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.name = name

    @loggable
    @Mitocondria.conn_handling
    def search_all(self, *args, **kwargs) -> List[Dict[str, str | int]]:
        cursor = self.conn.cursor()
        query_filepath = os.path.join(self.queries_folder_path,
                                      'search_all_muni.sql')
        with open(file=query_filepath, mode='r') as file:
            query = file.read()
        query = query.format(schema=self.schema)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        headers = [header[0] for header in cursor.description]
        result = [dict(zip(headers, row)) for row in result]

        return result

    @loggable
    def app_sync(self, *args, **kwargs):
        model = MuniMito
        munis = self.search_all()
        user_obj = User.objects.get(username=APP_USERNAME)

        objs = {obj.code: obj
                for obj in model.objects.all()}
        for muni in munis:
            code = str(muni['code'])
            name = muni['name']

            sync_kwargs = {'model': model}
            if code in objs:
                obj = objs[code]
                sync_func = bulk_update_with_history
                sync_kwargs['fields'] = [
                    'code',
                    'name',
                    'changed_by'
                ]
            else:
                sync_func = bulk_create_with_history
                obj = model()

            obj.code = code
            obj.name = name
            obj.changed_by = user_obj
            sync_kwargs['objs'] = [obj]
            sync_func(**sync_kwargs)
