from rest_framework.permissions import BasePermission

from helpers.user.permission import Permission


class EditDelivFormFromApiPermission(BasePermission):
    def has_permission(self, request, view, *args, **kwargs):
        user = request.user
        has_perm = Permission(user=user).can_edit_deliv_form_from_api()
        return has_perm
