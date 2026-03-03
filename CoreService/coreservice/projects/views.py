from dependency_injector.wiring import Provide, inject
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.containers.event import EventContainer
from core.enums.project_event import ProjectEvent
from core.enums.project_roles import ProjectRole
from core.enums.topics import TopicEnum
from core.kafka.event_service import EventService
from core.mixins import DynamicSerializerMixin
from projects.models import Project, UserProject
from projects.permissions import ProjectPermission
from projects.serializers import (
    ProjectCreateSerializer,
    ProjectGetSerializer,
    ProjectSaveUserSerializer,
    ProjectUpdateSerializer,
)


class ProjectViewSet(DynamicSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ProjectPermission]
    queryset = Project.objects.all()

    serializer_class = ProjectGetSerializer

    serializer_action_map = {
        "create": ProjectCreateSerializer,
        "update": ProjectUpdateSerializer,
        "partial_update": ProjectUpdateSerializer,
        "add_user": ProjectSaveUserSerializer,
        "update_user_role": ProjectSaveUserSerializer,
    }

    @inject
    def __init__(
        self,
        event_service: EventService = Provide[EventContainer.event_service],
        **kwargs,
    ):
        self.event_service = event_service
        super().__init__(**kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Project.objects.all()

        if not user.is_authenticated:
            return Project.objects.none()

        return Project.objects.filter(userproject__user=user).distinct()

    def perform_create(self, serializer):
        with transaction.atomic():
            project = serializer.save()
            user = self.request.user
            UserProject.objects.create(
                user=user,
                project=project,
                project_role=ProjectRole.OWNER.value,
            )

            self.event_service.send_event(
                TopicEnum.TOPIC.value,
                event_type=ProjectEvent.PROJECT_CREATED.value,
                status=project.status,
                user=user,
                producer="Project",
                data={
                    "project_id": str(project.id),
                    "title": project.name,
                },
            )

    def perform_update(self, serializer):
        project = serializer.save()
        user = self.request.user

        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=ProjectEvent.PROJECT_UPDATED.value,
            status=project.status,
            user=user,
            producer="Project",
            data={
                "project_id": str(project.id),
                "title": project.name,
            },
        )

    @action(detail=True, methods=["post"], url_path="user")
    def add_user(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"project": project})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Send Kafka event for user addition
        user = serializer.validated_data["user"]
        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=ProjectEvent.PROJECT_USER_ADDED.value,
            status=project.status,
            user=request.user,
            producer="Project",
            data={
                "project_id": str(project.id),
                "title": project.name,
                "assigned_user_id": str(user.id),
            },
        )

        return Response(
            ProjectGetSerializer(project).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["put", "patch"], url_path="user-role")
    def update_user_role(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get("user")
        user_project = get_object_or_404(UserProject, project=project, user=user_id)

        serializer = self.get_serializer(
            instance=user_project,
            data=request.data,
            context={"project": project},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(
            user_project,
            validated_data={"project_role": serializer.validated_data["project_role"]},
        )

        return Response(
            ProjectGetSerializer(project).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path=r"user/(?P<user_pk>[^/.]+)")
    def remove_user(self, request, pk: str = None, user_pk: str = None):
        project: Project = self.get_object()
        user_project = get_object_or_404(UserProject, project=project, user_id=user_pk)

        # Send Kafka event for user removal
        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=ProjectEvent.PROJECT_USER_REMOVED.value,
            status=project.status,
            user=request.user,
            producer="Project",
            data={
                "project_id": str(project.id),
                "title": project.name,
                "removed_user_id": str(user_pk),
            },
        )

        user_project.delete()

        return Response(
            ProjectGetSerializer(project).data,
            status=status.HTTP_200_OK,
        )
