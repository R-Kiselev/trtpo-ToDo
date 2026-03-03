from rest_framework.exceptions import PermissionDenied

from core.enums.project_roles import ProjectRole
from core.permission_base import PermissionBase
from projects.models import Project, UserProject


class ProjectPermission(PermissionBase):
    permission_prefix = "project"
    object_model = Project

    def _get_user_role(self, user, project: Project) -> ProjectRole:
        user_project = UserProject.objects.filter(user=user, project=project).get()

        if user_project is None:
            raise PermissionDenied("User is not associated with this project.", 403)

        user_role = user_project.project_role
        if user_role is None:
            raise PermissionDenied("User role is not defined for this project.", 403)
        return ProjectRole(user_role)
