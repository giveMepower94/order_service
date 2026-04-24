from dataclasses import dataclass
from datetime import datetime

from src.order_service.domain.enums import OrderStatus


@dataclass
class Order:
    id: str
    user_id: str
    item_id: str
    quantity: int
    status: OrderStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    