from src.order_service.infrastructure.clients.catalog import CatalogClient


def get_catalog_client() -> CatalogClient:
    return CatalogClient()
