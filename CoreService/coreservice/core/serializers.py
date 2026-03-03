from rest_framework import serializers

from core.models import User


class User(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "auth_id", "email")
