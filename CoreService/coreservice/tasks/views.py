from dependency_injector.wiring import Provide, inject
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.containers.event import EventContainer
from core.enums.task_event import TaskEvent
from core.enums.task_roles import TaskRole
from core.enums.topics import TopicEnum
from core.kafka.event_service import EventService
from core.mixins import DynamicSerializerMixin
from projects.models import Project
from tasks.models import Task, UserTask
from tasks.permissions import TaskPermission
from tasks.serializers import (
    TaskCreateSerializer,
    TaskGetSerializer,
    TaskSaveUserSerializer,
    TaskUpdateSerializer,
)
from tasks.tasks import send_email_to_assigned_user


class TaskViewSet(DynamicSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TaskPermission]
    queryset = Task.objects.all()

    serializer_class = TaskGetSerializer
    serializer_action_map = {
        "create": TaskCreateSerializer,
        "update": TaskUpdateSerializer,
        "partial_update": TaskUpdateSerializer,
        "add_user": TaskSaveUserSerializer,
        "update_user_role": TaskSaveUserSerializer,
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
            return Task.objects.all()
        if not user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(usertask__user=user).distinct()

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer = self.get_serializer(
                data=self.request.data, context={"request": self.request}
            )
            serializer.is_valid(raise_exception=True)

            task = serializer.save()
            user = self.request.user
            UserTask.objects.create(user=user, task=task, task_role=TaskRole.OWNER.value)

            project = Project.objects.get(id=task.project_id)

            self.event_service.send_event(
                TopicEnum.TOPIC.value,
                event_type=TaskEvent.TASK_CREATED.value,
                status=task.status,
                user=user,
                producer="Task",
                data={
                    "task_id": str(task.id),
                    "project_id": str(project.id),
                    "title": task.name,
                },
            )

    def perform_update(self, serializer):
        task = serializer.save()
        user = self.request.user
        project = Project.objects.get(id=task.project_id)

        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=TaskEvent.TASK_UPDATED.value,
            status=task.status,
            user=user,
            producer="Task",
            data={
                "task_id": str(task.id),
                "project_id": str(project.id),
                "title": task.name,
            },
        )

    @action(detail=True, methods=["post"], url_path="users")
    def add_user(self, request, pk=None):
        task = self.get_object()

        serializer = self.get_serializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = serializer.validated_data["user"]
        project = Project.objects.get(id=task.project_id)

        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=TaskEvent.TASK_USER_ADDED.value,
            status=task.status,
            user=request.user,
            producer="Task",
            data={
                "task_id": str(task.id),
                "project_id": str(project.id),
                "title": task.name,
                "assigned_user_id": str(user.id),
            },
        )

        # Celery task to send email
        send_email_to_assigned_user.delay(
            task_id=task.id,
            user_id=user.id,
        )

        return Response(
            TaskGetSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["put", "patch"], url_path="user-role")
    def update_user_role(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get("user")
        user_task = get_object_or_404(UserTask, task=task, user_id=user_id)

        serializer = self.get_serializer(
            instance=user_task,
            data=request.data,
            context={"task": task},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(
            TaskGetSerializer(task).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path=r"user/(?P<user_pk>[^/.]+)")
    def remove_user(self, request, pk: str = None, user_pk: str = None):
        task: Task = self.get_object()
        user_task = get_object_or_404(UserTask, task=task, user_id=user_pk)
        project = Project.objects.get(id=task.project_id)

        self.event_service.send_event(
            TopicEnum.TOPIC.value,
            event_type=TaskEvent.TASK_USER_REMOVED.value,
            status=task.status,
            user=request.user,
            producer="Task",
            data={
                "task_id": str(task.id),
                "project_id": str(project.id),
                "title": task.name,
                "removed_user_id": str(user_pk),
            },
        )

        user_task.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
