from multiprocessing import Queue

from dependency_injector import containers, providers

from core.kafka.event_service import EventService


class EventContainer(containers.DeclarativeContainer):
    queue = providers.Singleton(Queue)

    event_service = providers.Singleton(EventService, queue=queue)
