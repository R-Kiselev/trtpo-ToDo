from typing import Optional, Type

from django.db.models import Model
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from core.enums.base_role import RoleEnum
from core.models import Permission


class PermissionBase(BasePermission):
    object_model: Optional[Type[Model]] = None
    permission_prefix: Optional[str] = None

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Request, view: APIView, obj: Model) -> bool:
        if not self.object_model or not isinstance(obj, self.object_model):
            return False

        user = request.user

        if user.role == "admin":
            return True

        try:
            user_role = self._get_user_role(user, obj)
        except PermissionDenied as e:
            self.message = str(e)
            return False

        if not self.permission_prefix:
            self.message = "Permission configuration error."
            return False

        permission = Permission.objects.filter(name=f"{self.permission_prefix}.{view.action}").get()

        if user_role.value in permission.default_for:
            return True

    def _get_user_role(self, user, obj: Model) -> Optional[RoleEnum]:
        raise NotImplementedError("Subclasses must implement `_get_user_role`")
