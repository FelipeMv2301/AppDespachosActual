from django.urls import path

from app.delivery.views.review import ReviewView

urlpatterns = [
    path(route='delivery_review',
         view=ReviewView.as_view(),
         name='delivery_review'),
]
