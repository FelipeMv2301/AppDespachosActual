import os
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.generic.base import View
from simple_history.utils import bulk_update_with_history

from app.business_partner.models.contact import Contact
from app.delivery.forms.issue import IssueForm
from app.delivery.models.delivery import Delivery
from app.delivery.models.doc import Document
from app.delivery.models.doc_type import DocumentType as DocType
from app.delivery.models.doc_type_service import \
    DocumentTypeService as DocTypeServ
from app.delivery.models.opt import Option
from app.delivery.models.status import Status
from app.general.models.address import Address
from app.general.models.muni import Muni
from app.general.models.service_account import ServiceAccount
from app.order.models.delivery import OrderDelivery
from app.order.models.grouping import Grouping
from classes.starken.delivery import Delivery as StkDeliv
from config.settings.base import ALLOWED_PRIVATE_HOSTS
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable
from notification.email.order import OrderEmail

PAGE_TITLE = 'Creación de entregas'


class IssueView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'issue.html')
    form = IssueForm
    permission_required = ('delivery.issue_delivery')
    allowed_domains = ALLOWED_PRIVATE_HOSTS

    @domain_check(allowed_domains=allowed_domains)
    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        context = {'page_title': PAGE_TITLE,
                   'form': self.form()}

        return render(request=request,
                      template_name=self.template,
                      context=context)

    @domain_check(allowed_domains=allowed_domains)
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
        is_complete = f['is_complete'] == 'Y'
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
                  .select_related('order',
                                  'delivery_option',
                                  'addr',
                                  'customer',
                                  'contact')
                  .filter(code=group_code))
        first_group = groups.first()
        ordr_deliv = (OrderDelivery.objects
                      .filter(order_grouping=groups.first()))
        if ordr_deliv.exists():
            new_groups = []
            new_groups_code = Grouping.new_code()
            for orig_group in groups:
                new_groups.append(
                    Grouping.objects.create(
                        code=new_groups_code,
                        order=orig_group.order,
                        delivery_option=orig_group.delivery_option,
                        addr=orig_group.addr,
                        customer=orig_group.customer,
                        contact=orig_group.contact,
                        deliv_obs=orig_group.deliv_obs,
                        changed_by=user,
                    )
                )
            groups = new_groups
            first_group = groups[0]

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
            height=height or 0,
            width=width or 0,
            length=length or 0,
            weight=weight or 0,
            packages_qty=pack_qty or 0,
            valuation=valuation or 0,
            status=Status.objects.get(code='NOTISSUED'),
            is_complete=is_complete,
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

        if f['doc_folio']:
            docs = []
            for i, folio in enumerate(iterable=doc_folios):
                doc_type_code = doc_types[i]
                doc_type = DocType.objects.get(code=doc_type_code,
                                               enabled=True)
                doc_type_serv = (DocTypeServ.objects
                                 .filter(service_acct=acct,
                                         doc_type=doc_type,
                                         enabled=True)
                                 .first())
                Document.objects.create(folio=folio,
                                        type=doc_type,
                                        delivery=deliv,
                                        changed_by=user)
                docs.append({'type': doc_type,
                             'type_service': doc_type_serv,
                             'folio': folio})

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
            deliv.locked = True
            deliv.status = Status.objects.get(code='ISSUED')
            deliv.changed_by = user
            bulk_update_with_history(objs=[deliv],
                                     model=Delivery,
                                     fields=['folio',
                                             'rcpt_commit_date',
                                             'status',
                                             'changed_by',
                                             'locked'])
        else:
            deliv.issue_date = date.today()
            deliv.locked = True
            deliv.status = Status.objects.get(code='ISSUED')
            deliv.changed_by = user
            bulk_update_with_history(objs=[deliv],
                                     model=Delivery,
                                     fields=['issue_date',
                                             'status',
                                             'changed_by',
                                             'locked'])
        messages.success(request=request,
                         message=('¡Emisión hecha! Orden de entrega: '
                                  f'{deliv.folio}'))
        email = OrderEmail(delivery=deliv)
        email.send_email()

        return redirect(to='delivery_review')

        context['form'] = form_by_user
        return render(request=request,
                      template_name=self.template,
                      context=context)
