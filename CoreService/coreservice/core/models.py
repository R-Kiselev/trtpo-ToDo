from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.db import models


class Base(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class DateTimeMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class User(Base):
    auth_id = models.UUIDField(unique=True)
    email = models.EmailField(max_length=255, unique=True, null=False)

    def is_authenticated(self):
        """This is exactly what the built-in django User model does"""
        return True

    class Meta:
        db_table = "users"

    def __str__(self):
        return str(self.auth_id)


class Permission(Base):
    name = models.CharField(max_length=255, unique=True)
    default_for = ArrayField(
        models.CharField(max_length=20),
    )

    class Meta:
        db_table = "permissions"
