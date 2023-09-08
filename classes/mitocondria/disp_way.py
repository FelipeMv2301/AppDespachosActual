from classes.mitocondria.mitocondria import Mitocondria
# from app.order.models.municipality_mito import MunicipalityMito as MitoMuni
from helpers.decorator.loggable import loggable


class DispatchWay(Mitocondria):
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
    def search_all(self, *args, **kwargs) -> list:
        cursor = self.conn.cursor()
        query = 'SELECT st.despachos_param_tipo_entrega_id id,'
        query += 'st.despachos_param_tipo_entrega_nombre name '
        query += f'FROM {self.schema}.{self.ship_type_mdl} st'

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
    # def app_sync(self, *args, **kwargs) -> None:
    #     ways = self.ways_search()
    #     for w in ways:
    #         id = w["id"]
    #         name = w["name"]
    #         object_search = DispWayMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             DispWayMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)
