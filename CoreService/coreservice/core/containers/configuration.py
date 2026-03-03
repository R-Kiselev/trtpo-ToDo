from dependency_injector import containers, providers

from core.config import AuthConfig, EmailConfig, KafkaConfig


class AuthContainer(containers.DeclarativeContainer):
    config = providers.Factory(AuthConfig)


class EmailContainer(containers.DeclarativeContainer):
    config = providers.Factory(EmailConfig)


class KafkaContainer(containers.DeclarativeContainer):
    config = providers.Factory(KafkaConfig)
