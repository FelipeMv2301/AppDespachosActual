import os

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import View
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.business_partner.models.contact import Contact
from app.delivery.models.opt import Option
from app.general.models.address import Address
from app.general.models.muni import Muni
from app.order.forms.delivery_form import DeliveryForm
from app.order.models.grouping import Grouping
from app.order.models.order import Order
from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import CustomError

PAGE_TITLE = 'Formulario de entrega'


class DeliveryFormView(View):
    template = os.path.join('order', 'delivery_form.html')
    form = DeliveryForm

    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        context = {'page_title': PAGE_TITLE,
                   'form': self.form(user=request.user)}

        return render(request=request,
                      template_name=self.template,
                      context=context)

    @authentication
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        context = {'page_title': PAGE_TITLE}
        params = request.POST
        user = request.user
        form_by_user = self.form(data=params, user=request.user)
        if not form_by_user.is_valid():
            context['form'] = form_by_user
            messages.error(request=request,
                           message='Error al guardar')
            return render(request=request,
                          template_name=self.template,
                          context=context)

        f = form_by_user.cleaned_data
        ordr_doc_nums = f['orders'].split(',')
        contact_first_name = f['contact_first_name'] or None
        contact_last_name = f['contact_last_name'] or None
        contact_email_addr = f['contact_email_addr']
        contact_phone_number = f['contact_phone_number']
        deliv_st_and_num = f['deliv_st_and_num'] or None
        deliv_addr_complement = f['deliv_addr_complement'] or None
        deliv_muni_code = f['deliv_muni']
        carrier_code = f['carrier']
        deliv_type_code = f['deliv_type']
        deliv_service_code = f['deliv_service']
        deliv_pay_type_code = f['deliv_pay_type']
        branch_code = f['branch'] or None
        obs = f['obs']

        # Revisar si existe la opción de entrega
        try:
            opt = Option.objects.get(carrier__code=carrier_code,
                                     service__code=deliv_service_code,
                                     type__code=deliv_type_code,
                                     pay_type__code=deliv_pay_type_code,
                                     branch__code=branch_code)
        except Option.MultipleObjectsReturned:
            e_msg = 'Error: no existe una opción de envío definida'
            log_msg = e_msg + f'\nData: {f}'
            e = CustomError(msg=e_msg, log=log_msg)
            raise e
        except Option.DoesNotExist:
            e_msg = 'Error: no existe opción de envío'
            log_msg = e_msg + f'\nData: {f}'
            e = CustomError(msg=e_msg, log=log_msg)
            raise e

        # Valida que la sucursal disponga de entrega y corresponda a la comuna de destino
        if branch_code and (not opt.branch.delivery or
                            opt.branch.addr.muni.code != deliv_muni_code):
            e_msg = 'Error: La sucursal no dispone de entrega '
            e_msg += 'o no corresponde a la comuna'
            log_msg = e_msg + f'\nData: {f}'
            e = CustomError(msg=e_msg, log=log_msg)
            raise e

        # Valida que la comuna de destino existe
        try:
            muni = Muni.objects.get(code=deliv_muni_code)
        except Muni.MultipleObjectsReturned:
            e_msg = 'Error: no existe una comuna definida'
            log_msg = e_msg + f'\nData: {f}'
            e = CustomError(msg=e_msg, log=log_msg)
            raise e
        except Muni.DoesNotExist:
            e_msg = 'Error: no existe comuna'
            log_msg = e_msg + f'\nData: {f}'
            e = CustomError(msg=e_msg, log=log_msg)
            raise e

        # Revisar si existe la agrupación de pedidos
        group_query = Grouping.objects.filter(order__doc_num__in=ordr_doc_nums,
                                              enabled=True)
        grouped_data = (group_query
                        .values('code')
                        .annotate(code_count=Count('code')))
        group_result = grouped_data.filter(code_count=len(ordr_doc_nums))
        if group_result:
            group_code = group_result[0]['code']
            group = (Grouping.objects
                     .select_related('addr', 'contact')
                     .filter(code=group_code))
            ordrs = [g.order for g in group]
            first_group = group.first()
            cust = first_group.customer
            addr = Address.objects.get(id=first_group.addr.id)
            contact = Contact.objects.get(id=first_group.contact.id)
            group_func = bulk_update_with_history
            group_sync_objs = group
            group_sync_kwargs = {
                'model': Grouping,
                'fields': ['delivery_option',
                           'addr',
                           'customer',
                           'contact',
                           'deliv_obs',
                           'changed_by']
            }
        else:
            ordrs = Order.objects.filter(doc_num__in=ordr_doc_nums)
            if len(ordrs) != len(ordr_doc_nums):
                e_msg = 'Error: no existen los pedidos'
                log_msg = e_msg + f'\nData: {f}'
                e = CustomError(msg=e_msg, log=log_msg)
                raise e
            cust = ordrs.first().customer
            addr = Address.objects.create(
                st_and_num=deliv_st_and_num,
                complement=deliv_addr_complement,
                muni=muni,
                changed_by=user
            )
            contact = Contact.objects.create(
                first_name=contact_first_name,
                last_name=contact_last_name,
                addr=addr,
                mobile_phone=contact_phone_number,
                email_addr=contact_email_addr,
                changed_by=user
            )
            group_func = bulk_create_with_history
            group_sync_objs = []
            group_code = Grouping.new_code()
            for ordr in ordrs:
                group_sync_objs.append(Grouping(code=group_code, order=ordr))
            group_sync_kwargs = {'model': Grouping}

        for group_obj in group_sync_objs:
            group_obj.delivery_option = opt
            group_obj.addr = addr
            group_obj.customer = cust
            group_obj.contact = contact
            group_obj.deliv_obs = obs
            group_obj.changed_by = user
        group_sync_kwargs['objs'] = group_sync_objs
        group_func(**group_sync_kwargs)

        context['form'] = self.form(user=request.user)
        messages.success(request=request,
                         message='Guardado exitosamente')

        return render(request=request,
                      template_name=self.template,
                      context=context)
