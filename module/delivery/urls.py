from django.urls import path

from module.delivery.views.issue import IssueView
from module.delivery.views.kpis import KpisView
from module.delivery.views.panel import PanelView
from module.delivery.views.review import ReviewView
from module.delivery.views.track import TrackView

urlpatterns = [
    path(route='review',
         view=ReviewView.as_view(),
         name='delivery_review'),
    path(route='issue',
         view=IssueView.as_view(),
         name='delivery_issue'),
    path(route='kpis',
         view=KpisView.as_view(),
         name='deliv_kpis'),
    path(route='panel',
         view=PanelView.as_view(),
         name='deliv_panel'),
    path(route='track/<str:company_code>/<str:folio>',
         view=TrackView.as_view(),
         name='deliv_track'),
]
