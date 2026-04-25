from src.order_service.core.exceptions import OrderNotFoundError
from src.order_service.infrastructure.db.models import OrderModel
from src.order_service.infrastructure.repositories.orders import OrdersRepository


class GetOrderUseCase:
    def __init__(self, *, orders: OrdersRepository) -> None:
        self.orders = orders

    async def execute(self, order_id: str) -> OrderModel:
        order = await self.orders.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError("Order not found")

        return order
