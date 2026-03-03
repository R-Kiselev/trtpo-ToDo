from rest_framework import serializers

from core.enums.project_roles import ProjectRole
from core.enums.project_status import ProjectStatus
from core.models import User
from projects.models import Project, UserProject


class UserProjectSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project_role = serializers.ChoiceField(choices=ProjectRole.values())

    class Meta:
        model = UserProject
        fields = ("user", "project_role")


class ProjectGetSerializer(serializers.ModelSerializer):
    users = UserProjectSerializer(source="userproject_set", many=True, read_only=True)
    status = serializers.ChoiceField(choices=ProjectStatus.values())

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "done_at",
            "status",
            "created_at",
            "updated_at",
            "users",
        )


class ProjectCreateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=ProjectStatus.values(), default=ProjectStatus.PENDING.value
    )

    class Meta:
        model = Project
        fields = ("name", "description", "status")


class ProjectUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=ProjectStatus.values(), required=False)

    class Meta:
        model = Project
        fields = ("name", "description", "done_at", "status")


class ProjectSaveUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project_role = serializers.ChoiceField(
        choices=ProjectRole.values(), default=ProjectRole.READER.value
    )

    def validate(self, attrs):
        # Проверка на существование пользователя применяется только при создании
        if self.instance is None:  # Если это создание (нет instance)
            user = attrs["user"]
            project = self.context["project"]
            if UserProject.objects.filter(project=project, user=user).exists():
                raise serializers.ValidationError(
                    {"user": f"User '{user}' already exists in project '{project.name}'."}
                )
        return attrs

    def create(self, validated_data):
        project = self.context["project"]
        user_project_data = {
            "user": validated_data["user"].id,
            "project": project,
            "project_role": validated_data["project_role"],
        }
        user_project_serializer = UserProjectSerializer(data=user_project_data)
        user_project_serializer.is_valid(raise_exception=True)
        return user_project_serializer.save(project=project)

    def update(self, instance, validated_data):
        instance.project_role = validated_data.get("project_role", instance.project_role)
        instance.save()
        return instance
