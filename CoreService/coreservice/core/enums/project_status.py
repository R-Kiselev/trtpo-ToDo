from core.enums.base import BaseEnum


class ProjectStatus(BaseEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    CANCELLED = "Cancelled"
    DONE = "Done"
