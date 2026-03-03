from django.db import models

from core.enums.task_roles import TaskRole
from core.enums.task_status import TaskStatus
from core.models import Base, DateTimeMixin, User
from projects.models import Project


class Task(Base, DateTimeMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=255, choices=TaskStatus.choices(), default=TaskStatus.PENDING.value
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    class Meta:
        db_table = "tasks"


class UserTask(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_role = models.CharField(choices=TaskRole.choices(), default=TaskRole.READER.value)

    class Meta:
        db_table = "user_task"
        unique_together = ("user", "task")
