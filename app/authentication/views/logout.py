from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View

from app.general.models.user_session import UserSession


class Logout(View):
    def get(self, request):
        logout(request=request)
        session = UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key,
            end_time__isnull=True
        ).first()

        if session:
            session.end_time = timezone.now()
            session.save()

        return redirect(to='login')
