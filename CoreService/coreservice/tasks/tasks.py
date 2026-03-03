from celery import shared_task
from django.core.mail import send_mail

from core.containers.configuration import EmailContainer
from core.models import User
from tasks.models import Task

container = EmailContainer()


@shared_task
def send_email_to_assigned_user(task_id, user_id):
    email_config = container.config()
    task = Task.objects.get(id=task_id)
    user = User.objects.get(id=user_id)

    subject = f"Task assigned: {task.name}"
    message = (
        f"Task '{task.name}' has been assigned to you.\n\n"
        f"Description: {task.description}\n"
        f"Deadline: {task.deadline}\n"
    )

    send_mail(
        subject,
        message,
        email_config.email,
        [user.email],
        fail_silently=False,
    )
