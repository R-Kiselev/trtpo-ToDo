from django.db import migrations

from core.enums.project_roles import ProjectRole
from core.enums.task_roles import TaskRole

PROJECT_CONTROLLED_PERMISSIONS = [
    {
        "name": "project.read",
        "default_for": [
            ProjectRole.OWNER,
            ProjectRole.MAINTAINER,
            ProjectRole.READER,
        ],
    },
    {
        "name": "project.retrieve",
        "default_for": [
            ProjectRole.OWNER,
            ProjectRole.MAINTAINER,
            ProjectRole.READER,
        ],
    },
    {
        "name": "project.write",
        "default_for": [
            ProjectRole.OWNER,
            ProjectRole.MAINTAINER,
        ],
    },
    {
        "name": "project.update",
        "default_for": [
            ProjectRole.OWNER,
            ProjectRole.MAINTAINER,
        ],
    },
    {
        "name": "project.partial_update",
        "default_for": [
            ProjectRole.OWNER,
            ProjectRole.MAINTAINER,
        ],
    },
    {
        "name": "project.destroy",
        "default_for": [ProjectRole.OWNER],
    },
    {
        "name": "project.add_user",
        "default_for": [ProjectRole.OWNER, ProjectRole.MAINTAINER],
    },
    {
        "name": "project.update_user_role",
        "default_for": [ProjectRole.OWNER],
    },
    {
        "name": "project.remove_user",
        "default_for": [ProjectRole.OWNER],
    },
]

TASK_CONTROLLED_PERMISSIONS = [
    {
        "name": "task.read",
        "default_for": [
            TaskRole.OWNER,
            TaskRole.DEVELOPER,
            TaskRole.READER,
        ],
    },
    {
        "name": "task.retrieve",
        "default_for": [
            TaskRole.OWNER,
            TaskRole.DEVELOPER,
            TaskRole.READER,
        ],
    },
    {
        "name": "task.write",
        "default_for": [
            TaskRole.OWNER,
            TaskRole.DEVELOPER,
        ],
    },
    {
        "name": "task.update",
        "default_for": [
            TaskRole.OWNER,
            TaskRole.DEVELOPER,
        ],
    },
    {
        "name": "task.partial_update",
        "default_for": [
            TaskRole.OWNER,
            TaskRole.DEVELOPER,
        ],
    },
    {
        "name": "task.destroy",
        "default_for": [TaskRole.OWNER],
    },
    {
        "name": "task.add_user",
        "default_for": [TaskRole.OWNER, TaskRole.DEVELOPER],
    },
    {
        "name": "task.update_user_role",
        "default_for": [TaskRole.OWNER],
    },
    {
        "name": "task.remove_user",
        "default_for": [TaskRole.OWNER],
    },
]

ALL_PERMISSIONS = PROJECT_CONTROLLED_PERMISSIONS + TASK_CONTROLLED_PERMISSIONS


def add_permissions(apps, schema_editor):
    Permission = apps.get_model("core", "Permission")

    for perm in ALL_PERMISSIONS:
        default_for_str = [role.value for role in perm["default_for"]]
        Permission.objects.get_or_create(
            name=perm["name"], defaults={"default_for": default_for_str}
        )


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("core", "Permission")

    for perm in ALL_PERMISSIONS:
        try:
            Permission.objects.get(name=perm["name"]).delete()
        except Permission.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            code=add_permissions,
            reverse_code=remove_permissions,
        ),
    ]
