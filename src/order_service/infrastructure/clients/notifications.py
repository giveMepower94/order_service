import httpx
from pydantic import BaseModel

from src.order_service.core.config import settings
from src.order_service.core.exceptions import OrderServiceError


class NotificationCreateResponse(BaseModel):
    id: str
    user_id: str | None = None
    message: str
    reference_id: str


class NotificationsServiceError(OrderServiceError):
    pass


class NotificationsClient:
    def __init__(self) -> None:
        self.base_url = settings.capashino_base_url.strip().rstrip("/")
        self.api_key = settings.capashino_api_key.strip()

    async def send_notification(
        self,
        *,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> NotificationCreateResponse:
        url = f"{self.base_url}/api/notifications"

        payload = {
            "message": message,
            "reference_id": reference_id,
            "idempotency_key": idempotency_key,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"X-API-Key": self.api_key},
                )
                response.raise_for_status()
                return NotificationCreateResponse(**response.json())

        except httpx.HTTPError as exc:
            raise NotificationsServiceError(
                f"Notifications Service is unavailable: {type(exc).__name__}: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise NotificationsServiceError(
                f"Notifications Service error: {response.status_code}. {response.text[:300]}"
            )
        return NotificationCreateResponse.model_validate(response.json())
