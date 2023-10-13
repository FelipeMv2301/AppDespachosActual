from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=100)
    session_expiration = models.DateTimeField()

    class Meta:
        db_table = 'auth_user_session'
