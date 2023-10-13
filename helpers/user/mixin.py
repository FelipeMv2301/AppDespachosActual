from django.contrib.auth.mixins import PermissionRequiredMixin


class AnyPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        for permission in self.get_permission_required():
            if self.request.user.has_perm(permission):
                return True
        return False
