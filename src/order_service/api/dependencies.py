from src.order_service.infrastructure.clients.catalog import CatalogClient
from src.order_service.infrastructure.clients.payments import PaymentsClient


def get_catalog_client() -> CatalogClient:
    return CatalogClient()


def get_payments_client() -> PaymentsClient:
    return PaymentsClient()
