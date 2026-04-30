from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.infrastructure.db.models import OrderModel, OutboxMessageModel


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_order_paid(self, order: OrderModel) -> OutboxMessageModel:
        message = OutboxMessageModel(
            event_type="order.paid",

            payload={
                "event_type": "order.paid",
                "order_id": order.id,
                "item_id": order.item_id,
                "quantity": order.quantity,
                "idempotency_key": f"order-paid-{order.id}",
            },
            status="pending",
            attempts=0,
            created_at=datetime.now(timezone.utc)
        )

        self.session.add(message)
        await self.session.flush()
        return message

    async def list_pending(self, limit: int) -> list[OutboxMessageModel]:
        stmt = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.status == "pending")
            .order_by(OutboxMessageModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_sent(self, message: OutboxMessageModel) -> None:
        message.status = "sent"
        message.sent_at = datetime.now(timezone.utc)
        message.last_error = None
        await self.session.flush()

    async def mark_failed(self, message: OutboxMessageModel, error_text: str) -> None:
        message.attempts += 1
        message.last_error = error_text[:1000]
        await self.session.flush()
