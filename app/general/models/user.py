import traceback

from colorama import Fore, Style, init
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.db.utils import ProgrammingError
from django.dispatch import receiver
from django.utils import timezone

from core.settings.base import logger
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class UserProfile(models.Model):
    # General
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    initial_url = models.ForeignKey(to='general.Url',
                                    on_delete=models.CASCADE,
                                    null=True)
    # Object timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'auth_user_profile'

    def __str__(self):
        return self.user.username


@receiver(signal=post_save, sender=User)
def create_user_profile(sender, instance, created, *args, **kwargs):
    try:
        if created:
            UserProfile.objects.create(user=instance)
    except ProgrammingError:
        tb = traceback.format_exc()
        tb += f'User: {instance.username}'
        e_msg = f'{UNEXP_ERROR}\nUser: {instance.username}'
        CustomError(msg=e_msg, log=tb)
        init()
        logger.info(msg=(Style.BRIGHT + Fore.YELLOW +
                         'El error anterior está previsto'))
        Style.RESET_ALL
