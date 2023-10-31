import os

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import View
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from module.business_partner.models.contact import Contact
from module.delivery.models.opt import Option
from module.general.models.address import Address
from module.general.models.muni import Muni
from module.general.models.muni_service import MuniService
from module.order.forms.delivery_form import DeliveryForm
from module.order.models.grouping import Grouping
from module.order.models.order import Order
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from helpers.user.mixin import AnyPermissionRequiredMixin
from helpers.user.permission import Permission
from project.settings.base import ALLOWED_PRIVATE_HOSTS

PAGE_TITLE = 'Formulario de entrega'


class DeliveryFormView(AnyPermissionRequiredMixin, View):
    template = os.path.join('order', 'delivery_form.html')
    form = DeliveryForm
    permission_required = ('order.edit_commit_date',
                           'order.edit_all_order_delivery_form')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        user = request.user
        perm = Permission(user=user)
        can_edit_form = perm.can_edit_deliv_form()
        can_edit_commit_date = perm.can_edit_order_commit_date()

        context = {
            'page_title': PAGE_TITLE,
            'form': self.form(user=user,
                              can_edit_form=can_edit_form,
                              can_edit_commit_date=can_edit_commit_date),
            'can_edit_form': can_edit_form,
            'can_edit_commit_date': can_edit_commit_date,
        }

        return render(request=request,
                      template_name=self.template,
                      context=context)

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        user = request.user
        perm = Permission(user=user)
        can_edit_form = perm.can_edit_deliv_form()
        can_edit_commit_date = perm.can_edit_order_commit_date()

        params = request.POST
        form_by_user = self.form(data=params,
                                 user=request.user,
                                 can_edit_form=can_edit_form,
                                 can_edit_commit_date=can_edit_commit_date)

        context = {'page_title': PAGE_TITLE,
                   'can_edit_form': can_edit_form,
                   'can_edit_commit_date': can_edit_commit_date,
                   'form': form_by_user}
        if not form_by_user.is_valid():
            error_form_fields_to_delete = set()
            error_form_info_to_add = {}
            for field, error in form_by_user.errors.items():
                error_form_fields_to_delete.add(field)
                field_label = form_by_user.fields[field].label
                error_form_info_to_add[field_label] = error
            for field in error_form_fields_to_delete:
                form_by_user.errors.pop(field)
            for field, error in error_form_info_to_add.items():
                form_by_user.errors[field] = error

            context['form'] = form_by_user
            return render(request=request,
                          template_name=self.template,
                          context=context)

        f = form_by_user.cleaned_data
        ordr_doc_nums = f['orders'].split(',')

        ordrs = Order.objects.filter(doc_num__in=ordr_doc_nums)
        if len(ordrs) != len(ordr_doc_nums):
            messages.error(request=request,
                           message=('No existen todos o ninguno de los '
                                    'pedidos seleccionados'))
            return render(request=request,
                          template_name=self.template,
                          context=context)

        if can_edit_commit_date:
            commit_date = f['commit_date']
        if can_edit_form:
            contact_first_name = f['contact_first_name'] or None
            contact_last_name = f['contact_last_name'] or None
            contact_email_addr = f['contact_email_addr']
            contact_phone1 = f['contact_phone1']
            contact_phone2 = f['contact_phone2']
            contact_mobile_phone = f['contact_mobile_phone']
            if (not contact_phone1 and not contact_phone2 and
                    not contact_mobile_phone):
                messages.error(request=request,
                               message=('Debe ingresar al menos un número de '
                                        'teléfono'))
                return render(request=request,
                              template_name=self.template,
                              context=context)
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
                messages.error(request=request,
                               message=('No existe una opción de envío '
                                        'definida'))
                return render(request=request,
                              template_name=self.template,
                              context=context)
            except Option.DoesNotExist:
                messages.error(request=request,
                               message='No existe opción de envío')
                return render(request=request,
                              template_name=self.template,
                              context=context)

            muni_service = (MuniService.objects
                            .filter(service_acct__service=opt.carrier)
                            .first())
            if deliv_pay_type_code == 'CE':
                if muni_service and not muni_service.to_pay:
                    messages.error(request=request,
                                   message=('La comuna no acepta el tipo de '
                                            'pago'))
                    return render(request=request,
                                  template_name=self.template,
                                  context=context)

        if can_edit_commit_date:
            for ordr in ordrs:
                ordr.updtd_commit_date = commit_date or ordr.commit_date
                ordr.changed_by = user
                bulk_update_with_history(objs=ordrs,
                                         model=Order,
                                         fields=['updtd_commit_date',
                                                 'changed_by'])
        if can_edit_form:
            muni = Muni.objects.get(code=deliv_muni_code)
            # Revisar si existe la agrupación de pedidos
            group_query = Grouping.objects.filter(
                order__doc_num__in=ordr_doc_nums, enabled=True)
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
                addr.st_and_num = deliv_st_and_num
                addr.complement = deliv_addr_complement
                addr.muni = muni
                addr.changed_by = user
                bulk_update_with_history(objs=[addr],
                                         model=Address,
                                         fields=['st_and_num',
                                                 'complement',
                                                 'muni',
                                                 'changed_by'])
                contact = Contact.objects.get(id=first_group.contact.id)
                contact.first_name = contact_first_name
                contact.last_name = contact_last_name
                contact.email_addr = contact_email_addr
                contact.phone1 = contact_phone1
                contact.phone2 = contact_phone2
                contact.mobile_phone = contact_mobile_phone
                contact.changed_by = user
                bulk_update_with_history(objs=[contact],
                                         model=Contact,
                                         fields=['first_name',
                                                 'last_name',
                                                 'email_addr',
                                                 'phone1',
                                                 'phone2',
                                                 'mobile_phone',
                                                 'changed_by'])
                group_func = bulk_update_with_history
                group_sync_objs = group
                group_sync_kwargs = {'model': Grouping,
                                     'fields': ['delivery_option',
                                                'addr',
                                                'customer',
                                                'contact',
                                                'deliv_obs',
                                                'changed_by']}
            else:
                cust = ordrs.first().customer
                muni = Muni.objects.get(code=deliv_muni_code)
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
                    phone1=contact_phone1,
                    phone2=contact_phone2,
                    mobile_phone=contact_mobile_phone,
                    email_addr=contact_email_addr,
                    changed_by=user
                )
                group_func = bulk_create_with_history
                group_sync_objs = []
                group_code = Grouping.new_code()
                for ordr in ordrs:
                    group_sync_objs.append(Grouping(code=group_code,
                                                    order=ordr))
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

        context['form'] = self.form(user=request.user,
                                    can_edit_form=can_edit_form,
                                    can_edit_commit_date=can_edit_commit_date)
        messages.success(request=request,
                         message='Guardado exitosamente')

        return render(request=request,
                      template_name=self.template,
                      context=context)
