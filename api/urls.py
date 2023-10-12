from django.urls import path

from api.views.cancel_delivery import CancelDeliveryView
from api.views.check_auth import CheckAuthView
from api.views.deliv_opt_search import DelivOptSearchView
from api.views.order_group_search import OrderGroupSearchView
from api.views.order_search import OrderSearchView
from api.views.send_deliv_email import SendDelivEmailView
from api.views.upd_deliv_completion import UpdDelivCompletionView
from api.views.upd_deliv_rcpt_date import UpdDelivRcptDateView

urlpatterns = [
    path(route='v1/order/search',
         view=OrderSearchView.as_view(),
         name='order_search'),
    path(route='v1/order/group/search',
         view=OrderGroupSearchView.as_view(),
         name='order_group_search'),
    path(route='v1/delivery_option/search',
         view=DelivOptSearchView.as_view(),
         name='deliv_opt_search'),
    path(route='v1/auth/check',
         view=CheckAuthView.as_view(),
         name='check_auth'),
    path(route='v1/delivery/cancel/<str:folio>',
         view=CancelDeliveryView.as_view(),
         name='cancel_delivery'),
    path(route='v1/delivery/send_email/<str:folio>',
         view=SendDelivEmailView.as_view(),
         name='send_delivery_email'),
    path(route='v1/delivery/upd_completion/<str:folio>/<str:value>',
         view=UpdDelivCompletionView.as_view(),
         name='upd_deliv_completion'),
    path(route='v1/delivery/upd_rcpt_date/<str:folio>/<str:value>',
         view=UpdDelivRcptDateView.as_view(),
         name='upd_deliv_rcpt_date'),
]
