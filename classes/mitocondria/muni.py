from classes.mitocondria.mitocondria import Mitocondria
# from app.order.models.municipality_mito import MunicipalityMito as MitoMuni
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
    def search(self, *args, **kwargs) -> list:
        cursor = self.conn.cursor()
        query = 'SELECT muni.sys_comuna_id code, muni.sys_comuna_nombre name '
        query += f'FROM {self.schema}.{self.muni_mdl} muni'

        cursor.execute(query)
        results = cursor.fetchall()
        # TODO: check response
        description = cursor.description
        cursor.close()

        result = [
            dict(
                (description[i][0], value)
                for i, value in enumerate(row)
            ) for row in results
        ]

        return result

    # @loggable
    # def app_sync(self, *args, **kwargs) -> dict:
    #     munis = self.search()
    #     for m in munis:
    #         code = m['code']
    #         name = m['name']
    #         object_search = MitoMuni.objects.filter(code=code)

    #         if not object_search.exists():
    #             MitoMuni(name=name, code=code).save()
    #         else:
    #             object_search.update(name=name)
