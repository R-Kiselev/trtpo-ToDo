from typing import Dict, Optional, Type

from rest_framework.exceptions import APIException
from rest_framework.serializers import Serializer


class DynamicSerializerMixin:
    serializer_action_map: Optional[Dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        action_serializer = None
        if self.serializer_action_map:
            action_serializer = self.serializer_action_map.get(self.action)

        if action_serializer:
            return action_serializer

        if hasattr(self, "serializer_class") and self.serializer_class is not None:
            return super().get_serializer_class()
        else:
            raise APIException(
                f"Serializer class not found for action '{self.action}'\
                and no default 'serializer_class' defined on {self.__class__.__name__}."
            )
