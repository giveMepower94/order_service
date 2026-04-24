from decimal import Decimal

import httpx
from pydantic import BaseModel

from src.order_service.core.config import settings
from src.order_service.core.exceptions import CatalogServiceError


class CatalogItem(BaseModel):
    id: str
    name: str
    price: Decimal
    available_qty: int


class CatalogClient:
    def __init__(self):
        self.base_url = settings.capashino_base_url.rstrip("/")
        self.api_key = settings.capashino_api_key

    async def get_item(self, item_id: str) -> CatalogItem:
        url = f"{self.base_url}/api/catalog/items/{item_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    url,
                    headers={"X-API-Key": self.api_key},
                )
            except httpx.HTTPError as exc:
                raise CatalogServiceError("Catalog Service is unavailable") from exc

        if response.status_code == 404:
            raise CatalogServiceError("Item not found")

        if response.status_code >= 400:
            raise CatalogServiceError(
                f"Catalog Service error: {response.status_code}",
            )

        return CatalogItem.model_validate(response.json())
