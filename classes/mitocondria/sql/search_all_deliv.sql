SELECT 
    d.despacho_id id,
    d.nro_orden_flete folio,
    d.fecha_estimada_entrega commit_date,
    d.nombre_agencia_destino branch_name,
    d.created_on issue_date,
    dadm.alto height,
    dadm.ancho width,
    dadm.largo length,
    dadm.kilos_total weight,
    dadm.numero_bultos packages,
    dadm.valor_declarado valuation,
    CONCAT('[',
            GROUP_CONCAT(DISTINCT JSON_OBJECT('folio',
                        doc.n_documento,
                        'type',
                        doc_type.despachos_param_tipo_documento_id)),
            ']') docs,
    CONCAT('[',
        GROUP_CONCAT(DISTINCT JSON_OBJECT('ref', ordr.pedido_referencia)),
            ']') orders,
    -- ordr.pedido_total ordr_total_amt,
    -- ordr.pedido_impuesto ordr_total_tax,
    -- ordr.pedido_descuento ordr_total_disc,
    order_detail.direccion_destinatario ship_st_and_num,
    order_detail.comuna_destinatario ship_muni_name,
    order_detail.fono_destinatario phone_number,
    order_detail.email_destinatario email_addr,
    order_detail.nombre_contacto contact_name,
    -- order_detail.rut_cliente,
    order_detail.n_direccion ship_addr_cpl,
    order_detail.n_departamento ship_dpto,
    status.despacho_param_estado_id status_id,
    deliv_type.despachos_param_tipo_entrega_id  deliv_type_id,
    deliv_type.despachos_param_tipo_entrega_nombre deliv_type_name,
    pay_type.despachos_param_tipo_pago_id pay_type_id,
    pay_type.nombre_tipo_pago pay_type_name
FROM
    {schema}.ad_despachos d
        INNER JOIN
    {schema}.ad_despachos_admin dadm ON d.despachos_admin_id = dadm.despachos_admin_id
        LEFT JOIN
    {schema}.ad_despachos_doc_admin doc ON dadm.despachos_admin_id = doc.despachos_admin_id
        LEFT JOIN
    {schema}.ad_despachos_param_estado status ON d.despacho_param_estado_id = status.despacho_param_estado_id
        LEFT JOIN
    {schema}.ad_despachos_param_tipo_documento doc_type ON doc.despachos_param_tipo_documento_id = doc_type.despachos_param_tipo_documento_id
        INNER JOIN
    {schema}.ad_pedido_detalle order_detail ON dadm.pedido_detalle_id = order_detail.pedido_detalle_id
        INNER JOIN
    {schema}.ad_despachos_param_tipo_entrega deliv_type ON deliv_type.despachos_param_tipo_entrega_id = order_detail.despachos_param_tipo_entrega_id
        INNER JOIN
    {schema}.ad_despachos_param_tipo_pago pay_type ON pay_type.despachos_param_tipo_pago_id = order_detail.despachos_param_tipo_pago_id
        INNER JOIN
    {schema}.ad_pedido_pedidos_detalles ppd ON order_detail.pedido_detalle_id = ppd.pedido_detalle_id
        INNER JOIN
    {schema}.ad_pedido ordr ON ordr.pedido_id = ppd.pedido_id
WHERE
    d.created_on >= '{from_date}'
GROUP BY d.despacho_id
ORDER BY d.nro_orden_flete ASC