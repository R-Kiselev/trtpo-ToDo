import os
from multiprocessing import Process

from django.apps import AppConfig

from core.containers.configuration import AuthContainer, KafkaContainer
from core.containers.event import EventContainer
from core.kafka.kafka_producer import run_kafka_producer


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        packages = ["core", "tasks", "projects"]

        auth_container = AuthContainer()
        auth_container.wire(packages=packages)

        kafka_container = KafkaContainer()
        kafka_container.wire(packages=packages)

        event_container = EventContainer()
        event_container.wire(packages=packages)

        Process(
            target=run_kafka_producer,
            args=(
                event_container.queue(),
                kafka_container.config(),
            ),
            daemon=True,
        ).start()
