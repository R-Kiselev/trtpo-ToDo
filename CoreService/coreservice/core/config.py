import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AuthConfig:
    url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000/auth")


@dataclass
class EmailConfig:
    email: str = os.getenv("DEFAULT_FROM_EMAIL")


@dataclass
class KafkaConfig:
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
