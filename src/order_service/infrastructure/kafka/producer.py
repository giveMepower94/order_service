import json

from aiokafka import AIOKafkaProducer

from src.order_service.core.config import settings


class KafkaProducer:
    def __init__(self) -> None:
        self.bootstrap_servers = settings.kafka_bootstrap_servers.strip()
        self.topic = settings.order_events_topic.strip()

    async def send(self, payload: dict) -> None:
        producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )

        await producer.start()

        try:
            await producer.send_and_wait(self.topic, payload)
        finally:
            await producer.stop()
