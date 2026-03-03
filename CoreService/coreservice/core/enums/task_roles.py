from core.enums.base_role import RoleEnum


class TaskRole(RoleEnum):
    READER = "Reader"  # Read-only access
    DEVELOPER = "Developer"  # Read, write, update
    OWNER = "Owner"  # Read, write, update, delete
