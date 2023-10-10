import os

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic.base import View
from simple_history.utils import bulk_update_with_history

from app.business_partner.models.contact import Contact
from app.delivery.forms.issue import IssueForm
from app.delivery.models.delivery import Delivery
from app.delivery.models.doc import Document
from app.delivery.models.doc_type import DocumentType
from app.delivery.models.opt import Option
from app.delivery.models.status import Status
from app.general.models.address import Address
from app.general.models.muni import Muni
from app.general.models.service_account import ServiceAccount
from app.order.models.grouping import Grouping
from classes.starken.delivery import Delivery as StkDeliv
from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable

PAGE_TITLE = 'Creación de entregas'


class IssueView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'issue.html')
    form = IssueForm
    permission_required = ('delivery.issue_delivery')

    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        context = {'page_title': PAGE_TITLE,
                   'form': self.form()}

        return render(request=request,
                      template_name=self.template,
                      context=context)

    @authentication
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        context = {'page_title': PAGE_TITLE}
        user = request.user
        params = request.POST
        form_by_user = self.form(data=params)
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
        searched_orders = f['orders']
        group_code = f['group']
        acct_code = f['acct']
        contact_first_name = f['contact_first_name']
        contact_last_name = f['contact_last_name']
        contact_email_addr = f['contact_email_addr']
        contact_mobile_phone = f['contact_mobile_phone']
        deliv_st_and_num = f['deliv_st_and_num']
        deliv_addr_complement = f['deliv_addr_complement']
        muni_code = f['deliv_muni']
        carrier_code = f['carrier']
        deliv_type_code = f['deliv_type']
        deliv_service_code = f['deliv_service']
        deliv_pay_type_code = f['deliv_pay_type']
        branch_code = f['branch'] or None
        assy_date = f['assy_date']
        height = f['height']
        width = f['width']
        length = f['length']
        # volume = f['volume']
        weight = f['weight']
        pack_qty = f['pack_qty']
        valuation = f['valuation']
        doc_folios = params.getlist(key='doc_folio')
        doc_types = params.getlist('doc_type')
        context['form'] = form_by_user

        # Validación de la opción de entrega
        try:
            opt = Option.objects.get(
                carrier__code=carrier_code,
                service__code=deliv_service_code,
                type__code=deliv_type_code,
                pay_type__code=deliv_pay_type_code,
                branch__code=branch_code,
                enabled=True,
            )
        except Option.DoesNotExist:
            messages.error(request=request,
                           message='No existe opción de entrega')
            return render(request=request,
                          template_name=self.template,
                          context=context)
        except Option.MultipleObjectsReturned:
            messages.error(request=request,
                           message='No existe un opción de entrega definida')
            return render(request=request,
                          template_name=self.template,
                          context=context)

        acct = (ServiceAccount.objects
                .select_related('service')
                .get(code=acct_code, enabled=True))
        groups = (Grouping.objects
                  .select_related('addr', 'contact')
                  .filter(code=group_code, enabled=True))
        first_group = groups.first()
        addr_id = first_group.addr.id
        contact_id = first_group.contact.id

        muni = Muni.objects.get(code=muni_code)
        addr = Address.objects.get(id=addr_id)
        addr.st_and_num = deliv_st_and_num
        addr.complement = deliv_addr_complement
        addr.muni = muni
        addr.changed_by = user
        bulk_update_with_history(
            objs=[addr],
            model=Address,
            fields=['st_and_num', 'complement', 'muni', 'changed_by']
        )
        contact = Contact.objects.get(id=contact_id)
        contact.first_name = contact_first_name
        contact.last_name = contact_last_name
        contact.mobile_phone = contact_mobile_phone
        contact.email_addr = contact_email_addr
        contact.changed_by = user
        bulk_update_with_history(
            objs=[contact],
            model=Contact,
            fields=['first_name',
                    'last_name',
                    'mobile_phone',
                    'email_addr',
                    'changed_by']
        )

        deliv = Delivery.objects.create(
            service_acct=acct,
            assembly_date=assy_date,
            height=height,
            width=width,
            length=length,
            weight=weight,
            packages_qty=pack_qty,
            valuation=valuation,
            status=Status.objects.get(code='NOTISSUED'),
            changed_by=user,
        )
        for ordr_group in groups:
            ordr_group.delivery_option = opt
            ordr_group.enabled = False
            ordr_group.changed_by = user
            deliv.order_delivery.add(ordr_group)
        bulk_update_with_history(objs=groups,
                                 model=Grouping,
                                 fields=['delivery_option',
                                         'changed_by',
                                         'enabled'])

        docs = []
        for i, folio in enumerate(iterable=doc_folios):
            doc_type_code = doc_types[i]
            doc_type = DocumentType.objects.get(code=doc_type_code,
                                                enabled=True)
            Document.objects.create(folio=folio,
                                    type=doc_type,
                                    delivery=deliv,
                                    changed_by=user)
            docs.append({'type': doc_type, 'folio': folio})

        if acct.service.code == 'STK':
            stk_deliv = StkDeliv(account=acct)
            stk_deliv.issue(
                delivery=deliv,
                data={
                    'height': height,
                    'width': width,
                    'length': length,
                    'weight': weight,
                    'valuation': valuation,
                    'packg_qty': pack_qty,
                    'docs': docs
                }
            )
            deliv.folio = stk_deliv.folio
            deliv.rcpt_commit_date = stk_deliv.rcpt_commit_date
            deliv.issue_date = stk_deliv.issue_date
            deliv.locked = True
            deliv.status = Status.objects.get(code='ISSUED')
            deliv.changed_by = user
            bulk_update_with_history(objs=[deliv],
                                     model=Delivery,
                                     fields=['folio',
                                             'rcpt_commit_date',
                                             'issue_date',
                                             'status',
                                             'changed_by',
                                             'locked'])
            messages.success(request=request,
                             message=f'¡Emissión hecha! OT: {stk_deliv.folio}')
        else:
            pass
        # if not form_by_user.is_valid():
        #     context['form'] = form_by_user
        #     messages.error(request=request,
        #                    message='Error al guardar')
        #     return render(request=request,
        #                   template_name=self.template,
        #                   context=context)

        # f = form_by_user.cleaned_data
        # ordr_doc_nums = [str(doc_num)
        #                  for doc_num in searched_orders.split(',')]
        # ordr_delivs = [obj for obj in OrderDelivery.query_for_delivery_review(ordr_doc_nums=ordr_doc_nums)]
        # if not ordr_delivs:
        #     messages.error(request=request,
        #                    message='No se encontraron entregas asociadas')
        # else:
        #     context['ordr_delivs'] = ordr_delivs

        # context['searched_orders'] = searched_orders
        context['form'] = form_by_user
        return render(request=request,
                      template_name=self.template,
                      context=context)
