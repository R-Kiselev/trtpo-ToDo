from core.enums.base import BaseEnum


class TaskStatus(BaseEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    CANCELLED = "Cancelled"
    DONE = "Done"
