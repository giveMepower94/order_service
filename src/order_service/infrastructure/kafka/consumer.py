import json

from aiokafka import AIOKafkaConsumer

from src.order_service.core.config import settings
from src.order_service.domain.enums import OrderStatus
from src.order_service.infrastructure.db.session import AsyncSessionLocal
from src.order_service.infrastructure.repositories.inbox import InboxRepository
from src.order_service.infrastructure.repositories.orders import OrdersRepository
from src.order_service.application.usecases.send_order_notification import (
    send_order_notifications
)


SHIPMENT_EVENTS_TOPIC = "student_system-shipment.events"


async def handle_shipment_events(payload: dict):
    event_type = payload.get("event_type")
    order_id = payload.get("order_id")

    if not event_type or not order_id:
        print("Invalid payload: missing event_type or order_id")
        return

    event_id = (
        payload.get("event_id")
        or payload.get("shipment_id")
        or payload.get("idempotency_key")
    )

    async with AsyncSessionLocal() as session:
        inbox = InboxRepository(session)
        orders = OrdersRepository(session)

        if await inbox.exists(event_id):
            return

        order = await orders.get_by_id(order_id)

        if order is None:
            await inbox.save_processed(
                event_id=event_id,
                event_type=event_type,
                payload=payload
            )

            await session.commit()
            return

        if event_type == "order.shipped":
            await orders.update_status(order, OrderStatus.SHIPPED)
            await send_order_notifications(
                order_id=order.id,
                status=OrderStatus.SHIPPED.value,
            )

        elif event_type == "order.cancelled":
            await orders.update_status(order, OrderStatus.CANCELLED)
            await send_order_notifications(
                order_id=order.id,
                status=OrderStatus.CANCELLED.value,
                reason=payload.get("reason"),
            )

        await inbox.save_processed(
                event_id=event_id,
                event_type=event_type,
                payload=payload
            )

        await session.commit()


async def run_shipment_consumer() -> None:
    consumer = AIOKafkaConsumer(
        SHIPMENT_EVENTS_TOPIC,
        bootstrap_servers=settings.kafka_bootstrap_servers.strip(),
        group_id="student-givemepower94-order-service",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    await consumer.start()
    print("SHIPMENT CONSUMER: started")

    try:
        async for message in consumer:
            print(f"SHIPMENT CONSUMER: received {message.value}")
            await handle_shipment_events(message.value)
    finally:
        await consumer.stop()
