# core/authentication.py
import requests
from dependency_injector.wiring import Provide, inject
from django.db import IntegrityError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.containers.configuration import AuthContainer
from core.models import User


class JWTAuthentication(BaseAuthentication):
    @inject
    def authenticate(self, request, config: AuthContainer = Provide[AuthContainer.config]):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            response = requests.get(
                f"{config.url}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                verify=False,
            )

            if response.status_code == 500:
                raise AuthenticationFailed(
                    "Authentication service is unavailable",
                    code=500,
                )

            response.raise_for_status()
            user_data = response.json()
        except requests.RequestException:
            raise AuthenticationFailed("Invalid token", code=401)

        auth_id = user_data.get("id")
        auth_email = user_data.get("email")

        if not auth_id:
            raise AuthenticationFailed("User ID not found in auth data", code=500)

        user = self.get_or_create_user(auth_id, auth_email)
        user.role = user_data.get("role")

        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"

    def get_or_create_user(self, auth_id, auth_email):
        try:
            user, created = User.objects.get_or_create(auth_id=auth_id, email=auth_email)
            return user
        except IntegrityError:
            raise AuthenticationFailed("User creation failed")
