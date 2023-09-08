from classes.mitocondria.mitocondria import Mitocondria
# from app.order.models.municipality_mito import MunicipalityMito as MitoMuni
from helpers.decorator.loggable import loggable


class DispatchPayType(Mitocondria):
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
        query = 'SELECT d.despachos_param_tipo_pago_id id,'
        query += 'd.nombre_tipo_pago name '
        query += f'FROM {self.schema}.{self.ship_pay_type_mdl} d'

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
    #     types = self.pay_types_search()
    #     for t in types:
    #         id = t['id']
    #         name = t['name']
    #         object_search = ShipPayTypeMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             ShipPayTypeMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)
