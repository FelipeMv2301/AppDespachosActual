from django.urls import path

from api.views.check_auth import CheckAuthView
from api.views.deliv_opt_search import DelivOptSearchView
from api.views.order_search import OrderSearchView

urlpatterns = [
    path(route='v1/order/search',
         view=OrderSearchView.as_view(),
         name='order_search'),
    path(route='v1/delivery_option/search',
         view=DelivOptSearchView.as_view(),
         name='deliv_opt_search'),
    path(route='v1/auth/check',
         view=CheckAuthView.as_view(),
         name='check_auth'),
]
