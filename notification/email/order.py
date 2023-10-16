import os
import re
import traceback
from typing import Sequence

from django.db.models import CharField, F, Value
from django.db.models.functions import Coalesce, Concat
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from app.delivery.models.delivery import Delivery
from app.order.models.delivery import OrderDelivery
from config.settings.base import EMAIL_HOST_USER, env
from helpers.error.custom_error import CustomError
from notification.email.email import ATTACHMENTS_PATH, Email


class OrderEmail(Email):
    def __init__(self,
                 delivery: Delivery,
                 subject: str = '📢 Notificación de estado de su pedido',
                 cc: Sequence[str] = None,
                 bcc: Sequence[str] = None,
                 *args, **kwargs):
        self.reply_to = env.list(var='DELIV_EMAIL_ADDR')

        cc_recipients = env.list(var='NOTIF_EMAIL_RECIPIENTS')
        if cc:
            cc_recipients.extend(cc)
        self.cc = cc_recipients

        self.delivery = delivery
        try:
            deliv_query = (
                OrderDelivery.objects
                .filter(delivery=delivery)
                        # order_grouping__delivery_option__type__typeservice__service_acct=delivery.service_acct,
                        # order_grouping__delivery_option__pay_type__paytypeservice__service_acct=delivery.service_acct)
                .values(
                    deliv_id=F('delivery__id'),
                    folio=F('delivery__folio'),
                    deliv_status_code=F('delivery__status__code'),
                    deliv_type_code=F('order_grouping__delivery_option__type__code'),
                    carrier_code=F('delivery__service_acct__service__code'),
                    carrier_name=F('delivery__service_acct__service__name'),
                    company_trade_name=F('delivery__service_acct__company__trade_name'),
                    company_code=F('delivery__service_acct__company__code'),
                    order_doc_num=F('order_grouping__order__doc_num'),
                    branch_addr=Concat('order_grouping__delivery_option__branch__addr__st_and_num',
                                    Value(' '),
                                    'order_grouping__delivery_option__branch__addr__complement',
                                    output_field=CharField()),
                    branch_addr_maps_url=F('order_grouping__delivery_option__branch__addr__maps_url'),
                    branch_hours=F('order_grouping__delivery_option__branch__hours'),
                    rcpt_commit_date=F('delivery__rcpt_commit_date'),
                    email_addr=F('order_grouping__contact__email_addr'),
                    contact_name=Concat(Coalesce('order_grouping__contact__first_name', Value('')),
                                        Value(' '),
                                        Coalesce('order_grouping__contact__first_name', Value('')),
                                        output_field=CharField()),
                ).distinct()
            )
            self.deliv_query = deliv_query.first()
        except Exception:
            tb = traceback.format_exc()
            tb += f'Delivery folio: {delivery.folio}'
            tb += f'Delivery id: {delivery.id}'
            e_msg = 'Error: Ha ocurrido un error en el envío de correo'
            e_msg += f'Delivery folio: {delivery.folio}'
            e = CustomError(msg=e_msg, log=tb)
            raise e

        if self.deliv_query['deliv_status_code'] != 'ISSUED':
            e_msg = 'Error: Ha ocurrido un error en el envío de correo. '
            e_msg = 'No corresponde el envío de correo por el estado'
            e_msg += f'Delivery folio: {delivery.folio}'
            e = CustomError(msg=e_msg)
            raise e

        self.from_email = re.sub(pattern=r'[^a-zA-Z0-9\s]',
                                 repl='',
                                 string=self.deliv_query['company_trade_name'])
        self.from_email += f' <{EMAIL_HOST_USER}>'

        ordr_doc_nums = ', '.join([deliv['order_doc_num']
                                   for deliv in deliv_query])
        tmpl_context = {
            'contact_name': self.deliv_query['contact_name'],
            'order_doc_num': ordr_doc_nums,
            'branch_addr_maps_url': self.deliv_query['branch_addr_maps_url'],
            'branch_address': self.deliv_query['branch_addr'],
            'branch_hours': self.deliv_query['branch_hours'],
            'company_code': self.deliv_query['company_code'],
            'company_trade_name': self.deliv_query['company_trade_name'],
            'track_url': '',
        }

        self.attachs = []
        if (self.deliv_query['carrier_code'] == 'STK' or
                self.deliv_query['deliv_type_code'] == 'HOMEDELIV'):
            filepath_template = 'order_shipped.html'
            tmpl_context.update({
                'folio': self.deliv_query['folio'],
                'carrier_name': self.deliv_query['carrier_name'],
                'deliv_type_code': self.deliv_query['deliv_type_code'],
            })
            self.attachs = [{
                'filepath': 'dispatch_insurance.pdf',
                'filename': 'Seguro de envío.pdf'
            }]
        elif (self.deliv_query['carrier_code'] == 'BQ' or
              self.deliv_query['carrier_code'] == 'TD'):
            filepath_template = 'order_pickup.html'
        else:
            e_msg = 'Error: Ha ocurrido un error en el envío de correo. '
            e_msg = 'No se pudo definir el tipo de correo'
            e_msg += f'Delivery folio: {delivery.folio}'
            e = CustomError(msg=e_msg)
            raise e

        for attch in self.attachs:
            filepath = attch['filepath']
            filepath = os.path.join(ATTACHMENTS_PATH, filepath)
            attch['filepath'] = filepath
            with open(file=filepath, mode='rb') as f:
                attch['content'] = f.read()

        self.subject = f'{subject}: {ordr_doc_nums}'
        template = render_to_string(template_name=filepath_template,
                                    context=tmpl_context)
        self.body = strip_tags(value=template)
        self.body = template

        super().__init__(to=['ti@bioquimica.cl'],
                         subject=self.subject,
                         from_email=self.from_email,
                         body=self.body,
                         body_content_type='html',
                         cc=self.cc,
                         bcc=bcc,
                         reply_to=self.reply_to,
                         attachments=self.attachs,
                         *args,
                         **kwargs)

    def send_email(self):
        try:
            self.send()
        except Exception:
            tb = traceback.format_exc()
            tb += f'Delivery folio: {self.delivery.folio}'
            tb += f'Delivery id: {self.delivery.id}'
            e_msg = 'Error: Ha ocurrido un error en el envío de correo'
            e_msg += f'Delivery folio: {self.delivery.folio}'
            e = CustomError(msg=e_msg, log=tb)
            raise e
