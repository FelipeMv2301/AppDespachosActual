from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View


class Logout(View):
    def get(self, request):
        logout(request=request)
        return redirect(to='login')
