import os

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic.base import View

from app.delivery.forms.review import ReviewForm
from app.order.models.delivery import OrderDelivery
from config.settings.base import ALLOWED_PRIVATE_HOSTS
from helpers.decorator.auth import authentication
from helpers.decorator.domain import domain_check
from helpers.decorator.loggable import loggable

PAGE_TITLE = 'Entregas'


class ReviewView(PermissionRequiredMixin, View):
    template = os.path.join('delivery', 'review.html')
    form = ReviewForm
    permission_required = ('delivery.view_delivery')
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
        params = request.POST
        form_by_user = self.form(data=params)
        if not form_by_user.is_valid():
            context['form'] = form_by_user
            messages.error(request=request,
                           message='Error al guardar')
            return render(request=request,
                          template_name=self.template,
                          context=context)

        f = form_by_user.cleaned_data
        searched_orders = f['orders']
        ordr_doc_nums = [str(doc_num)
                         for doc_num in searched_orders.split(',')]
        ordr_delivs = [obj for obj in OrderDelivery.query_for_delivery_review(ordr_doc_nums=ordr_doc_nums)]
        if not ordr_delivs:
            messages.error(request=request,
                           message='No se encontraron entregas asociadas')
        else:
            context['ordr_delivs'] = ordr_delivs

        context['form'] = self.form()
        context['searched_orders'] = searched_orders
        return render(request=request,
                      template_name=self.template,
                      context=context)
