from django.urls import path

from app.delivery.views.issue import IssueView
from app.delivery.views.review import ReviewView

urlpatterns = [
    path(route='review',
         view=ReviewView.as_view(),
         name='delivery_review'),
    path(route='issue',
         view=IssueView.as_view(),
         name='delivery_issue'),
]
