from django.contrib.auth.models import User
from django.db.models import Q
from simple_history.utils import bulk_update_with_history

from classes.mitocondria.mitocondria import Mitocondria
# from app.dispatch.models.dispatch import Dispatch as DispModel
# from app.dispatch.models.dispatch_way_equivalence import \
#     DispatchWayEquivalence as DispWayEq
# from app.dispatch.models.dispatch_way_mito import \
#     DispatchWayMito as DispWayMito
# from app.dispatch.models.shipping_pay_type_mito import \
#     ShippingPayTypeMito as ShipPayTypeMito
# from app.order.models.municipality_equivalence import \
#     MunicipalityEquivalence as MuniEq
# from app.order.models.order import Order
# from app.order.templatetags.order_tags import remove_none_value
from helpers.decorator.loggable import loggable


class Dispatch(Mitocondria):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @loggable
    @Mitocondria.conn_handling
    def search_with_orders(self, from_date: str, *args, **kwargs) -> dict:
        cursor = self.conn.cursor()
        schema = self.schema
        query = 'SELECT d.despacho_id id,'
        query += 'CAST(d.nro_orden_flete as char) folio,'
        query += 'SUBSTRING(CAST(d.created_on as char), 1, 10) assembly_date,'
        query += 'CAST(d.fecha_estimada_entrega as char) reception_commitment_date,'
        query += 'CAST(p.pedido_referencia as char) order_reference,'
        query += 'CAST(p.pedido_tipo_id as char) order_type,'
        query += 'CASE WHEN (co.sys_comuna_id is null) THEN "13118" ELSE co.sys_comuna_id END municipality_code,'
        query += "CONCAT_WS (' ', pd.direccion_destinatario, pd.n_direccion, pd.n_departamento) street,"
        query += "te.despachos_param_tipo_entrega_id way_id,"
        query += "pd.fono_destinatario client_phone,"
        query += "pd.email_destinatario client_email,"
        query += "pd.nombre_contacto contact_name,"
        query += "pd.nota_cliente client_obs "
        query += f"FROM {schema}.{self.disp_mdl} d "
        query += f"INNER JOIN {schema}.{self.disp_order_mdl} dp ON "
        query += "d.despacho_id = dp.despacho_id "
        query += f"INNER JOIN {schema}.{self.order_order_details_mdl} ppd ON "
        query += "dp.pedido_pedidos_detalle_id = ppd.pedido_pedidos_detalles_id "
        query += f"INNER JOIN {schema}.{self.order_mdl} p ON ppd.pedido_id = p.pedido_id "
        query += f"INNER JOIN {schema}.{self.order_details_mdl} pd ON "
        query += "ppd.pedido_detalle_id = pd.pedido_detalle_id "
        query += f"LEFT JOIN {schema}.{self.muni_mdl} co ON "
        query += "pd.comuna_destinatario = co.sys_comuna_nombre "
        query += f"LEFT JOIN {schema}.{self.ship_type_mdl} te ON "
        query += "pd.despachos_param_tipo_entrega_id = te.despachos_param_tipo_entrega_id "
        query += f"WHERE d.created_on >= '{from_date}'"
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
    # def app_sync(self, from_date: str, *args, **kwargs) -> None:
    #     app_user = User.objects.get(username='django')

    #     dispatches = self.search_with_orders(from_date=from_date)

    #     for d in dispatches:
    #         id = d['id']
    #         folio = d['folio']
    #         if str(folio) == '0':
    #             folio = DispModel.new_folio()
    #         assembly_date = d['assembly_date']
    #         reception_commitment_date = d['reception_commitment_date']
    #         order_reference = d['order_reference']
    #         municipality_code = d['municipality_code']
    #         street = d['street']
    #         way_id = str(d['way_id'])
    #         client_phone_number = d['client_phone']
    #         client_email = d['client_email']
    #         contact_name = d['contact_name']
    #         client_observations = remove_none_value(d['client_obs'])
    #         municipality_object = MuniEq.objects.filter(
    #             mito_municipality__code=municipality_code
    #         ).first().municipality
    #         way_object = DispWayEq.objects.filter(
    #             mito_way__code=way_id
    #         ).first().app_way
    #         if d['order_type'] == '2':
    #             order_object = Order.objects.filter(
    #                 web_order_reference=order_reference
    #             )
    #         else:
    #             order_object = Order.objects.filter(reference=order_reference)
    #         if order_object:
    #             objs = order_object
    #             for obj in objs:
    #                 obj.dispatch_municipality = municipality_object
    #                 obj.dispatch_street = street
    #                 obj.client_phone_number = client_phone_number
    #                 obj.client_email = client_email
    #                 obj.contact_name = contact_name
    #                 obj.client_observations = client_observations
    #                 obj.changed_by = app_user
    #                 bulk_update_with_history(
    #                     objs,
    #                     Order,
    #                         [
    #                         'dispatch_municipality',
    #                         'dispatch_street',
    #                         'client_phone_number',
    #                         'client_email',
    #                         'contact_name',
    #                         'client_observations',
    #                         'changed_by'
    #                     ]
    #                 )
    #             dispatch_object = DispModel.objects.filter(
    #                 Q(mitocondria_id=id) &
    #                 Q(order__reference=order_reference)
    #             )
    #             if dispatch_object:
    #                 objs = dispatch_object
    #                 for obj in objs:
    #                     obj.assembly_date = assembly_date
    #                     obj.reception_commitment_date = reception_commitment_date
    #                     obj.from_mito = True
    #                     obj.from_app = False
    #                     obj.order = order_object[0]
    #                     obj.dispatch_way = way_object
    #                     obj.dispatch_municipality = municipality_object
    #                     obj.dispatch_street = street
    #                     obj.locked = True
    #                     obj.changed_by = app_user
    #                     bulk_update_with_history(
    #                         objs,
    #                         DispModel,
    #                         [
    #                             'assembly_date',
    #                             'reception_commitment_date',
    #                             'from_mito',
    #                             'from_app',
    #                             'order',
    #                             'dispatch_way',
    #                             'dispatch_municipality',
    #                             'dispatch_street',
    #                             'locked',
    #                             'changed_by'
    #                         ]
    #                     )
    #             else:
    #                 DispModel.objects.create(
    #                     folio=folio,
    #                     assembly_date=assembly_date,
    #                     dispatch_date=assembly_date,
    #                     from_mito=True,
    #                     from_app=False,
    #                     status=DispModel.Status.DISPATCHED,
    #                     order=order_object[0],
    #                     dispatch_way=way_object,
    #                     dispatch_municipality=municipality_object,
    #                     dispatch_street=street,
    #                     mitocondria_id=id,
    #                     locked=True,
    #                     changed_by=app_user
    #                 ).save()

    # @loggable
    # def ways_search(self, *args, **kwargs) -> dict:
    #     cursor = self.connection.cursor()
    #     query = (
    #         "SELECT d.despachos_param_tipo_entrega_id id,"
    #         "d.despachos_param_tipo_entrega_nombre name "
    #         f"FROM {self.schema}.{self.shipping_type_model} d"
    #     )
    #     cursor.execute(query)
    #     results = cursor.fetchall()
    #     description = cursor.description
    #     cursor.close()
    #     self.disconnect()
    #     myresult = [
    #         dict(
    #             (description[i][0], value)
    #             for i, value in enumerate(row)
    #         ) for row in results
    #     ]

    #     return myresult

    # @loggable
    # def ways_sync(self, *args, **kwargs) -> None:
    #     ways = self.ways_search()
    #     for w in ways:
    #         id = w["id"]
    #         name = w["name"]
    #         object_search = DispWayMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             DispWayMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)

    # @loggable
    # def pay_types_search(self, *args, **kwargs) -> dict:
    #     cursor = self.connection.cursor()
    #     query = (
    #         "SELECT d.despachos_param_tipo_pago_id id,"
    #         "d.nombre_tipo_pago name "
    #         f"FROM {self.schema}.{self.shipping_pay_type_model} d"
    #     )
    #     cursor.execute(query)
    #     results = cursor.fetchall()
    #     description = cursor.description
    #     cursor.close()
    #     self.disconnect()
    #     myresult = [
    #         dict(
    #             (description[i][0], value)
    #             for i, value in enumerate(row)
    #         ) for row in results
    #     ]

    #     return myresult

    # @loggable
    # def pay_types_sync(self, *args, **kwargs) -> None:
    #     types = self.pay_types_search()
    #     for t in types:
    #         id = t['id']
    #         name = t['name']
    #         object_search = ShipPayTypeMito.objects.filter(name=name)

    #         if not object_search.exists():
    #             ShipPayTypeMito(name=name, code=id).save()
    #         else:
    #             object_search.update(name=name)
