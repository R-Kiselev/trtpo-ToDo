from json import dumps
from multiprocessing import Queue


class EventService:
    def __init__(self, queue: Queue):
        self.queue = queue

    def send_event(
        self,
        topic: str,
        event_type: str,
        status: str,
        user,
        producer: str,
        data: dict,
    ):
        event = {
            "topic": topic,
            "value": {
                "event_type": event_type,
                "status": status,
                "user_id": str(user.id),
                "producer": producer,
                "data": data,
            },
        }
        encoded_event = dumps(event).encode()
        self.queue.put(encoded_event)
