from core.enums.base_role import RoleEnum


class ProjectRole(RoleEnum):
    READER = "Reader"  # Read-only access
    MAINTAINER = "Maintainer"  # Read, write, update
    OWNER = "Owner"  # Read, write, update, delete
