import json
import os

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic.base import View

from app.order.forms.delivery_form import DeliveryForm
from app.order.models.order import Order
from helpers.decorator.auth import authentication
from helpers.decorator.loggable import loggable

PAGE_TITLE = 'Formulario de despachos'


class DeliveryFormView(View):
    template = os.path.join('order', 'delivery_form.html')
    form = DeliveryForm

    @authentication
    @loggable
    def get(self, request: WSGIRequest, *args, **kwargs):
        orders = [o.doc_num for o in Order.objects.all()]
        context = {'page_title': PAGE_TITLE,
                   'form': self.form(user=request.user),
                   'orders': json.dumps(obj=orders)}

        return render(request=request,
                      template_name=self.template,
                      context=context)

    @authentication
    @loggable
    def post(self, request: WSGIRequest, *args, **kwargs):
        params = request.POST
        print(params)
        print(self.form(data=params, user=request.user).is_valid())
        context = {'page_title': PAGE_TITLE,
                   'form': self.form(user=request.user)}
        # dated_form = form(data=params)
        # if dated_form.is_valid():
        #     cleaned_form = dated_form.clean()
        #     instance = Order.objects.filter(
        #         reference=cleaned_form.get('order')
        #     ).first()
        #     form(data=params, instance=instance).save()
        #     messages.success(
        #         request=request,
        #         message='Guardado exitosamente'
        #     )

        return render(request=request,
                      template_name=self.template,
                      context=context)
