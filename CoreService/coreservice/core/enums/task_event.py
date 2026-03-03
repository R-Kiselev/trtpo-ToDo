from enum import Enum


class TaskEvent(Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_USER_ADDED = "task_user_added"
    TASK_USER_REMOVED = "task_user_removed"
