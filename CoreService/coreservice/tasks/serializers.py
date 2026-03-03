from rest_framework import serializers

from core.enums.task_roles import TaskRole
from core.enums.task_status import TaskStatus
from core.models import User
from projects.models import Project
from tasks.models import Task, UserTask


class UserTaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    task_role = serializers.ChoiceField(choices=TaskRole.values())

    class Meta:
        model = UserTask
        fields = ("user", "task_role")


class TaskGetSerializer(serializers.ModelSerializer):
    users = UserTaskSerializer(source="usertask_set", many=True, read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    status = serializers.ChoiceField(choices=TaskStatus.values())

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "deadline",
            "done_at",
            "status",
            "created_at",
            "updated_at",
            "project",
            "users",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=TaskStatus.values(), default=TaskStatus.PENDING.value)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Task
        fields = ("name", "description", "deadline", "project", "status")

    def validate_project(self, project):
        user = self.context["request"].user
        if not project.userproject_set.filter(user=user).exists():
            raise serializers.ValidationError(
                f"User '{user}' is not associated with project '{project.name}'."
            )
        return project


class TaskUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=TaskStatus.values(), required=False)

    class Meta:
        model = Task
        fields = ("name", "description", "deadline", "done_at", "status")


class TaskSaveUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    task_role = serializers.ChoiceField(
        choices=TaskRole.values(),
        default=TaskRole.READER.value,
    )

    def validate(self, attrs):

        if self.instance is None:
            user = attrs["user"]
            task = self.context["task"]
            if UserTask.objects.filter(user=user, task=task).exists():
                raise serializers.ValidationError(
                    {"user": f"User '{user}' already exists in task '{task.name}'."}
                )
        return attrs

    def create(self, validated_data):
        task = self.context["task"]
        user_task_data = {
            "user": validated_data["user"].id,
            "task": task,
            "task_role": validated_data["task_role"],
        }
        user_task_serializer = UserTaskSerializer(data=user_task_data)
        user_task_serializer.is_valid(raise_exception=True)
        return user_task_serializer.save(task=task)

    def update(self, instance, validated_data):
        instance.task_role = validated_data.get("task_role", instance.task_role)
        instance.save()
        return instance
