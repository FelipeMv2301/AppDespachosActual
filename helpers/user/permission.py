from typing import Collection

from django.contrib.auth.models import User
from django.utils.functional import SimpleLazyObject

from helpers.decorator.loggable import loggable


class Permission:
    def __init__(self, user: User | SimpleLazyObject, *args, **kwargs):
        self.user = user

    @loggable
    def __check_perms(self, perms: Collection[str], *args, **kwargs) -> bool:
        return self.user.has_perms(perm_list=perms)

    @loggable
    def can_edit_order_commit_date(self) -> bool:
        perms = ['order.edit_commit_date']
        return self.__check_perms(perms=perms)

    @loggable
    def can_edit_deliv_form(self) -> bool:
        perms = ['order.edit_all_order_delivery_form']
        return self.__check_perms(perms=perms)
