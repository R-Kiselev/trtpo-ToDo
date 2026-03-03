from enum import Enum


class ProjectEvent(Enum):
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_USER_ADDED = "project_user_added"
    PROJECT_USER_REMOVED = "project_user_removed"
