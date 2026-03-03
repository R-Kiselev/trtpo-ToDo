from django.db import models

from core.enums.project_roles import ProjectRole
from core.enums.project_status import ProjectStatus
from core.models import Base, DateTimeMixin, User


class Project(Base, DateTimeMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(choices=ProjectStatus.choices(), default=ProjectStatus.PENDING.value)

    users = models.ManyToManyField(
        User,
        through="UserProject",
    )

    class Meta:
        db_table = "projects"


class UserProject(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_role = models.CharField(choices=ProjectRole.choices(), default=ProjectRole.READER.value)

    class Meta:
        db_table = "user_project"
        unique_together = ("user", "project")
