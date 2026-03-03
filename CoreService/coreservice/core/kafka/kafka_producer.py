import logging
import sys
from json import JSONDecodeError, dumps, loads
from multiprocessing import Queue

from confluent_kafka import KafkaError, Producer

from core.config import KafkaConfig

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def extract_message_info(message):
    logger.info(f"[Kafka Producer] Message received: {message}")

    if message is None:
        logger.info("[Kafka Producer] Received None")
        raise JSONDecodeError("Received None")

    event = loads(message.decode("utf-8"))
    topic = event["topic"]
    value = event["value"]
    value = dumps(value).encode("utf-8")

    return topic, value


def run_kafka_producer(
    queue: Queue,
    config: KafkaConfig,
):
    logger.info("[Kafka Producer] Starting Kafka producer...")
    producer = Producer(
        {
            "bootstrap.servers": config.bootstrap_servers,
        }
    )

    while True:
        try:
            message = queue.get()

            topic, value = extract_message_info(message)

            logger.info(f"[Kafka Producer] Sending event to topic '{topic}' with value '{value}'")
            producer.produce(
                topic,
                value=value,
            )
        except JSONDecodeError as e:
            logger.error(f"[Kafka Producer] JSONDecodeError: {e}")
        except KafkaError as e:
            logger.exception(f"[Kafka Producer] Error {e}")
