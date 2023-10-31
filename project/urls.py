"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from project.views.home import home

urlpatterns = [
    path(route='admin/', view=admin.site.urls),
    path(route='__debug__/', view=include(debug_toolbar.urls)),
    path(route='', view=home, name='home'),
    path(route='api/', view=include(arg='api.urls')),
    path(route='auth/', view=include(arg='module.authentication.urls')),
    path(route='order/', view=include(arg='module.order.urls')),
    path(route='delivery/', view=include(arg='module.delivery.urls')),
]

# Errors handling
handler403 = 'project.views.error_403.error_403'
handler404 = 'project.views.error_404.error_404'
handler500 = 'project.views.error_500.error_500'
