from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.core.exceptions import ItemNotAvailableError
from src.order_service.infrastructure.clients.catalog import CatalogClient
from src.order_service.infrastructure.db.models import OrderModel
from src.order_service.infrastructure.repositories.orders import OrdersRepository


class CreateOrderUseCase:
    def __init__(
        self,
        *,
        session: AsyncSession,
        orders: OrdersRepository,
        catalog_client: CatalogClient
    ) -> None:
        self.session = session
        self.orders = orders
        self.catalog_client = catalog_client

    async def execute(
        self,
        *,
        user_id: str,
        item_id: str,
        quantity: int,
        idempotency_key: str,
    ) -> OrderModel:
        existing_order = await self.orders.get_by_idempotency_key(idempotency_key)
        if existing_order is not None:
            return existing_order

        item = await self.catalog_client.get_item(item_id)

        if item.available_qty < quantity:
            raise ItemNotAvailableError("Not enough items in stock")

        order = await self.orders.create(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
            idempotency_key=idempotency_key,
        )

        await self.session.commit()
        await self.session.refresh(order)

        return order
