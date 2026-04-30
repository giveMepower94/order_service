from src.order_service.core.config import settings
from src.order_service.infrastructure.db.session import AsyncSessionLocal
from src.order_service.infrastructure.kafka.producer import KafkaProducer
from src.order_service.infrastructure.repositories.outbox import OutboxRepository


async def process_outbox_batch() -> None:
    async with AsyncSessionLocal() as session:
        outbox = OutboxRepository(session)
        producer = KafkaProducer()

        messages = await outbox.list_pending(settings.outbox_batch_size)

        for message in messages:
            try:
                await producer.send(message.payload)
                await outbox.mark_sent(message)
            except Exception as exc:
                await outbox.mark_failed(message, str(exc))

        await session.commit()
