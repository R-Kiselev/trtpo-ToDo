from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    user: str
    password: str
    port: str
    host: str
    db: str
    url: PostgresDsn

    # Connection parameters
    pool_size: int = 5
    max_overflow: int = 10

    # Debugging options
    echo: bool = False
    echo_pool: bool = False


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env-template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    postgres: DatabaseConfig
    jwt: JWTConfig
