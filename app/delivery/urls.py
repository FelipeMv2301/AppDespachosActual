from django.urls import path

from app.delivery.views.issue import IssueView
from app.delivery.views.kpis import KpisView
from app.delivery.views.panel import PanelView
from app.delivery.views.review import ReviewView

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
]
