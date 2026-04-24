from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.domain.enums import OrderStatus
from src.order_service.infrastructure.db.models import OrderModel


class OrdersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: str) -> OrderModel:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        results = await self.session.execute(stmt)
        return results.scalar_one_or_none()

    async def get_by_idempotency_key(
        self,
        idempotency_key: str
    ) -> OrderModel | None:
        stmt = select(OrderModel).where(
            OrderModel.idempotency_key == idempotency_key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: str,
        item_id: str,
        quantity: int,
        idempotency_key: str,
    ) -> OrderModel:
        order = OrderModel(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
            status=OrderStatus.NEW.value,
            idempotency_key=idempotency_key,
        )
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order
