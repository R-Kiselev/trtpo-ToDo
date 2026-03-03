from auth.models import Users
from auth.schemas import (
    JWTResponseSchema,
    TokenSchema,
    UserLoginSchema,
    UserPayloadSchema,
)
from auth.utils import (
    decode_token,
    generate_tokens,
    is_password_matching,
)
from exceptions import (
    PermissionDeniedError,
)
from settings import Settings


# Left all methods as static methods because they are not dependent on instance state
class UserService:
    @staticmethod
    async def login(
        user_login_data: UserLoginSchema, user: Users, settings: Settings
    ) -> JWTResponseSchema:
        if not user.is_active:
            raise PermissionDeniedError("User is blocked")
        if not is_password_matching(user_login_data.password, user.password):
            raise PermissionDeniedError("Invalid password")

        user_data = UserPayloadSchema.model_validate(user)
        jwt_response = generate_tokens(user_data, settings.jwt)

        return jwt_response

    @staticmethod
    async def refresh_token(refresh_token: TokenSchema, settings: Settings) -> JWTResponseSchema:
        payload = decode_token(refresh_token.token, settings.jwt)
        user_payload = UserPayloadSchema.model_validate(payload)
        jwt_response = generate_tokens(user_payload, settings.jwt)

        return jwt_response

    @staticmethod
    def verify_token(
        token: TokenSchema,
        settings: Settings,
    ) -> JWTResponseSchema:
        payload = decode_token(token.token, settings.jwt)

        return payload
