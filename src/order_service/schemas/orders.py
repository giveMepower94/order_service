from datetime import datetime

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    user_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    item_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class OrderResponse(BaseModel):
    id: str
    user_id: str
    quantity: int
    item_id: str
    status: str
    created_at: datetime
    updated_at: datetime
