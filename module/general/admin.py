from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from module.general.models.user_profile import UserProfile


class UserProfileInLine(admin.StackedInline):
    model = UserProfile
    can_delete = False


class AccountsUserAdmin(UserAdmin):
    inlines = [UserProfileInLine]


admin.site.unregister(model_or_iterable=User)
admin.site.register(model_or_iterable=User, admin_class=AccountsUserAdmin)
