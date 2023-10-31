from django.urls import path

from module.authentication.views.change_password import ChangePassword
from module.authentication.views.login import Login
from module.authentication.views.logout import Logout

urlpatterns = [
    path(route='', view=Login.as_view(), name='login'),
    path(route='logout', view=Logout.as_view(), name='logout'),
    path(route='password',
         view=ChangePassword.as_view(),
         name='change_password'),
]
