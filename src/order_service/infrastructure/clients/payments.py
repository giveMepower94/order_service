from decimal import Decimal

import httpx
from pydantic import BaseModel

from src.order_service.core.config import settings
from src.order_service.core.exceptions import OrderServiceError


class PaymentCreateResponse(BaseModel):
    id: str
    user_id: str | None = None
    order_id: str
    amount: Decimal
    status: str
    idempotency_key: str


class PaymentsServiceError(OrderServiceError):
    pass


class PaymentsClient:
    def __init__(self) -> None:
        self.base_url = settings.capashino_base_url.strip().rstrip("/")
        self.api_key = settings.capashino_api_key.strip()

    async def create_payment(
        self,
        *,
        order_id: str,
        amount: Decimal,
        callback_url: str,
        idempotency_key: str,
    ) -> PaymentCreateResponse:

        url = f"{self.base_url}/api/payments"
        payload = {
            "order_id": order_id,
            "amount": str(amount),
            "callback_url": callback_url,
            "idempotency_key": idempotency_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"X-API-Key": self.api_key},
                )
        except httpx.HTTPError as exc:
            raise PaymentsServiceError(
                f"Payments Service is unavailable: {type(exc).__name__}: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise PaymentsServiceError(
                f"Payments Service error: {response.status_code}. {response.text[:300]}"
            )

        return PaymentCreateResponse.model_validate(response.json())
