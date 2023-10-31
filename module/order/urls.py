from django.urls import path

from module.order.views.delivery_form import DeliveryFormView

urlpatterns = [
    path(route='delivery_form',
         view=DeliveryFormView.as_view(),
         name='delivery_form'),
]
