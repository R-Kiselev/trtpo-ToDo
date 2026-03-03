from typing import Optional

from rest_framework.exceptions import PermissionDenied

from core.enums.task_roles import TaskRole
from core.permission_base import PermissionBase
from tasks.models import Task, UserTask


class TaskPermission(PermissionBase):
    permission_prefix = "task"
    object_model = Task

    def _get_user_role(self, user, task: Task) -> Optional[TaskRole]:
        user_task = UserTask.objects.filter(user=user, task=task).get()

        if user_task is None:
            raise PermissionDenied("User is not associated with this task.", 403)

        user_role = user_task.task_role
        if user_role is None:
            raise PermissionDenied("User role is not defined for this task.", 403)

        return TaskRole(user_role)
