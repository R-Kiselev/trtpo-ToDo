from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from core.containers.configuration import EmailContainer
from core.enums.project_roles import ProjectRole
from core.enums.task_status import TaskStatus
from projects.models import UserProject

container = EmailContainer()


@shared_task
def send_reports_to_owners():
    email_config = container.config()

    user_projects = UserProject.objects.filter(project_role=ProjectRole.OWNER.value).all()

    for user_project in user_projects:
        user = user_project.user
        project = user_project.project

        tasks = project.tasks.all()
        total_tasks = tasks.count()

        if total_tasks == 0:
            continue

        pending_tasks = tasks.filter(status=TaskStatus.PENDING.value).count()
        in_progress_tasks = tasks.filter(status=TaskStatus.IN_PROGRESS.value).count()
        done_tasks = tasks.filter(status=TaskStatus.DONE.value).count()

        overdue_tasks = tasks.filter(
            deadline__lt=timezone.now(),
            status__in=[
                TaskStatus.PENDING.value,
                TaskStatus.IN_PROGRESS.value,
            ],
        ).count()

        progress = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0

        subject = f"Ежечасный отчет по проекту: {project.name}"
        message = (
            f"Отчет по проекту '{project.name}' на "
            f"{timezone.now().strftime('%Y-%m-%d %H:%M')}:\n\n"
            f"Всего задач: {total_tasks}\n"
            f"- В ожидании: {pending_tasks}\n"
            f"- В процессе: {in_progress_tasks}\n"
            f"- Завершено: {done_tasks}\n"
            f"Просроченных задач: {overdue_tasks}\n"
            f"Прогресс проекта: {progress:.2f}%\n\n"
        )

        send_mail(
            subject,
            message,
            email_config.email,
            [user.email],
            fail_silently=False,
        )
