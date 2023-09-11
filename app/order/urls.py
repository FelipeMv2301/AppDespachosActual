from django.urls import path

from app.authentication.views.change_password import ChangePassword
from app.authentication.views.login import Login
from app.authentication.views.logout import Logout

urlpatterns = [
    path(route='', view=Login.as_view(), name='login'),
    path(route='logout', view=Logout.as_view(), name='logout'),
    path(route='password',
         view=ChangePassword.as_view(),
         name='change_password'),
]
