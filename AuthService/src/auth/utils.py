from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import bcrypt
import jwt
from fastapi import Request

from auth.schemas import JWTResponseSchema, UserPayloadSchema
from exceptions import (
    InvalidOrExpiredTokenError,
)
from settings import JWTConfig


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def is_password_matching(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_page_url(request: Request, page_num: int) -> str:
    """Return URL with new page_num query parameter"""
    url = str(request.base_url) + str(request.url.path).lstrip("/")

    query_params = request.query_params._dict.copy()
    query_params["page_number"] = page_num
    encoded_query_string = urlencode(query_params)

    return f"{url}?{encoded_query_string}"


def generate_token(
    user_payload: UserPayloadSchema,
    settings: JWTConfig,
    expires_delta: int,
) -> str:
    token_payload = user_payload.model_dump(mode="json")
    token_payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_delta)

    encoded_jwt = jwt.encode(token_payload, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def generate_access_token(
    user_payload: UserPayloadSchema,
    settings: JWTConfig,
):
    return generate_token(
        user_payload=user_payload,
        settings=settings,
        expires_delta=settings.access_token_expire_minutes,
    )


def generate_refresh_token(
    user_payload: UserPayloadSchema,
    settings: JWTConfig,
):
    return generate_token(
        user_payload=user_payload,
        settings=settings,
        expires_delta=settings.refresh_token_expire_minutes,
    )


def decode_token(
    token: str,
    settings: JWTConfig,
) -> dict:
    try:
        decoded_jwt = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return decoded_jwt
    except jwt.PyJWTError as e:
        raise InvalidOrExpiredTokenError(e.__str__())


def generate_tokens(user_data: UserPayloadSchema, settings: JWTConfig) -> JWTResponseSchema:
    access_token = generate_access_token(user_data, settings)
    refresh_token = generate_refresh_token(user_data, settings)

    jwt_response = JWTResponseSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

    return jwt_response
